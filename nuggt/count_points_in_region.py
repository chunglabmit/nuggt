"""count_points_in_region

Count the number of points that fall into each region of a brain atlas.
"""

import argparse
import json
import numpy as np
import sys
import tifffile

from .brain_regions import BrainRegions
from nuggt.utils.warp import Warper


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--points",
                        help="The points to be counted",
                        required=True)
    parser.add_argument("--alignment",
                        help="The points file from nuggt-align",
                        required=True)
    parser.add_argument("--reference-segmentation",
                        help="The reference segmentation that we map to.",
                        required=True)
    parser.add_argument("--brain-regions-csv",
                        help="The .csv file that provides the correspondences "
                        "between segmentation IDs and their brain region names",
                        required=True)
    parser.add_argument("--output",
                        help="The name of the .csv file to be written",
                        required=True)
    parser.add_argument("--output-points",
                        help="The name of a points file that will hold the "
                        "input points transformed into the reference space.")
    parser.add_argument("--level",
                        help="The granularity level (1 to 8 with 8 as the "
                             "finest level.",
                        type=int,
                        default=8)
    parser.add_argument("--xyz",
                        help="Specify this flag if the points file is "
                        "ordered by X, Y, and Z instead of Z, Y and X.",
                        action="store_true")
    parser.add_argument("--exclude-empty",
                        action="store_true",
                        help="Exclude regions from the CSV that have no points"
                        " in them")
    return parser.parse_args(args)


def warp_points(pts_moving, pts_reference, points):
    """Warp points from the moving space to the reference

    :param pts_moving: points for aligning in the moving coordinate frame
    :param pts_reference: corresponding points in the reference frame
    :param points: the points to be translated
    :return: the points in the reference frame
    """
    warper = Warper(pts_moving, pts_reference)
    return warper(points)


def main():
    args = parse_args()
    with open(args.points) as fd:
        points = np.array(json.load(fd))
    if args.xyz:
        points = points[:, ::-1]
    with open(args.alignment) as fd:
        alignment = json.load(fd)
    moving_pts = np.array(alignment["moving"])
    ref_pts = np.array(alignment["reference"])
    xform = warp_points(moving_pts, ref_pts, points)
    if args.output_points is not None:
        if args.xyz:
            xformt = xform[:, ::-1]
        else:
            xformt = xform
        with open(args.output_points, "w") as fd:
            json.dump(xformt.tolist(), fd)
    xform = (xform + .5).astype(int)
    seg = tifffile.imread(args.reference_segmentation).astype(np.uint32)
    mask = np.all((xform >= 0) & (xform < np.array(seg.shape).reshape(1, 3)), 1)
    xform_legal = xform[mask]
    counts = np.bincount(
        seg[xform_legal[:, 0], xform_legal[:, 1], xform_legal[:, 2]])
    counts[0] += np.sum(~ mask)
    seg_ids = np.where(counts > 0)[0]
    counts_per_id = counts[seg_ids]

    with open(args.brain_regions_csv) as fd:
        br = BrainRegions.parse(fd)

    areas = np.bincount(seg.flatten(),
                        minlength=np.max(list(br.name_per_id.keys()))+1)
    d = {}
    area_d = {}
    level_max = np.max(list(br.id_level.values()))
    all_ids = sorted(br.name_per_id.keys())
    for level in range(level_max, -1, -1):
        for seg_id in all_ids:
            if br.id_level[seg_id] == level:
                if seg_id in area_d:
                    area_d[seg_id] = area_d[seg_id] + areas[seg_id]
                else:
                    area_d[seg_id] = areas[seg_id]
                if seg_id in br.parent_per_id:
                    parent_id = br.parent_per_id[seg_id]
                    if parent_id in area_d:
                        area_d[parent_id] = area_d[parent_id] + area_d[seg_id]
                    else:
                        area_d[parent_id] = area_d[seg_id]
    level = args.level + 1
    if not args.exclude_empty:
        for seg_id in all_ids:
            if br.id_level[seg_id] == level:
                d[seg_id] = 0

    for seg_id, count in zip(seg_ids, counts_per_id):
        try:
            level_id = br.level_per_id[seg_id][level]
        except:
            assert br.id_level[seg_id] < level
            continue
        if level_id in d:
            count += d[level_id]
        d[level_id] = count
    with open(args.output, "w") as fd:
        fd.write('"id","region","count","area","density"\n')
        for level_id in sorted(d):
            try:
                name = br.get_name(level_id)
            except:
                name = "background" if level_id == 0 \
                    else "region # %d" % level_id
            if area_d[level_id] == 0:
                density = 0
            else:
                density = d[level_id] * 1000 / area_d[level_id]
            fd.write('%d,"%s",%d,%d,%.06f\n' %
                     (level_id, name, d[level_id], area_d[level_id],
                      density))


if __name__=="__main__":
    main()
