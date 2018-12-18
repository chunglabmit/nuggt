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
                        help="The granularity level (1 to 7 with 7 as the "
                             "finest level. Default is the finest.",
                        type=int,
                        default=7)
    parser.add_argument("--xyz",
                        help="Specify this flag if the points file is "
                        "ordered by X, Y, and Z instead of Z, Y and X.",
                        action="store_true")
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

    if args.level == 7:
        with open(args.output, "w") as fd:
            fd.write('"id","region","count"\n')
            for seg_id, count in zip(seg_ids, counts_per_id):
                if seg_id == 0:
                    region = "not in any region"
                else:
                    region = br.name_per_id.get(seg_id, "id%d" % seg_id)
                fd.write('%d,"%s",%d\n' % (seg_id, region, count))
    else:
        d = {}
        for seg_id, count in zip(seg_ids, counts_per_id):
            level = br.get_level_name(seg_id, args.level)
            if level in d:
                count += d[level]
            else:
                d[level] = count
        with open(args.output, "w") as fd:
            fd.write('"region","count"\n')
            for level in sorted(d):
                fd.write('"%s",%d\n' % (level, d[level]))


if __name__=="__main__":
    main()
