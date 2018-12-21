import argparse
import glob
import json
import multiprocessing
import numpy as np
import os
import sys
import tifffile
import tqdm

from phathom.utils import SharedMemory

#
# Turn off MKL multiprocessing if installed:
# http://mvdoc.me/2017/disabling-multithreading-for-numpy-scikit-learn-etc-in-conda.html
#
try:
    import mkl
    mkl.set_num_threads(1)
except:
    pass

from .brain_regions import BrainRegions
from nuggt.utils.warp import Warper


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        help="The glob expression for the stack to be "
                        "measured",
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
                        action="append",
                        required=True)
    parser.add_argument("--level",
                        type=int,
                        help="The granularity level (1 to 7 with 7 as the "
                             "finest level. Default is the finest.",
                        action="append")
    parser.add_argument("--n-cores",
                        type=int,
                        default=os.cpu_count(),
                        help="The number of processes to use")
    parser.add_argument("--shrink",
                        type=int,
                        default=1,
                        help="How much to downsample the image coordinates "
                        "when transforming them to the segmentation "
                        "coordinate system.")
    parser.add_argument("--grid-size",
                        type=int,
                        default=100,
                        help="The number of knots in the bicubic spline grid "
                        "(in the x and y directions) used to approximate the "
                        "transformation")

    return parser.parse_args(args)


def do_plane(filename:str, z:int, segmentation: SharedMemory, warper:Warper,
             shrink=(1, 1), grid_size=(100, 100)):
    """Process one plane

    :param filename: the name of the tiff file holding the plane
    :param z: The z-coordinate of the tiff file
    :param segmentation: the shared-memory holder of the segmentation.
    :param shrink: The factor to shrink the warping in the y and x direction
    :param grid_size: the number of voxels between knots in the bspline grid
    :return: a two tuple of the counts per region and total intensities per
    region.
    """
    if np.isscalar(shrink):
        shrink = (shrink, shrink, shrink)
    if np.isscalar(grid_size):
        grid_size = (grid_size, grid_size)
    plane = tifffile.imread(filename)
    #
    # zz, yy and xx are the coordinates that we will convert via the warper.
    # We subsample to reduce the runtime and because the segmentation is
    # so much smaller than the image that subsampling has little effect on
    # accuracy.
    #
    zz, yy, xx = [_.flatten() for _ in
                  np.mgrid[z:z+1,
                           0:plane.shape[0]:shrink[0],
                           0:plane.shape[1]:shrink[1]]]
    yyy, xxx = np.mgrid[0:plane.shape[0],
                        0:plane.shape[1]]
    #
    # yyy and xxx are the translations from the dimensions of the plane to
    # the dimensions of the zz, yy, xx.
    #
    yyy = (yyy // shrink[0]).astype(np.uint32)
    xxx = (xxx // shrink[1]).astype(np.uint32)
    awarper = warper.approximate(
        np.array([z-1, z, z+1]),
        np.linspace(0, plane.shape[0] - 1, grid_size[0]),
        np.linspace(0, plane.shape[1] - 1, grid_size[1]))
    zseg, yseg, xseg = awarper(np.column_stack((zz, yy, xx))).transpose()
    zseg = np.round(zseg).astype(np.int32)
    yseg = np.round(yseg).astype(np.int32)
    xseg = np.round(xseg).astype(np.int32)
    mask = (xseg >= 0) & (xseg < segmentation.shape[2]) &\
           (yseg >= 0) & (yseg < segmentation.shape[1]) &\
           (zseg >= 0) & (zseg < segmentation.shape[0])
    with segmentation.txn() as m:
        send = np.max(m) + 1
        seg = m[zseg[mask], yseg[mask], xseg[mask]]
    orig_shape = ((plane.shape[0] + shrink[0] - 1) // shrink[0],
                  (plane.shape[1] + shrink[1] - 1) // shrink[1])
    oseg = np.zeros(orig_shape, seg.dtype)
    oseg[mask.reshape(orig_shape)] = seg
    seg = oseg[yyy, xxx]
    counts = np.bincount(seg.flatten(), minlength=send)
    sums = np.bincount(seg.flatten(), plane.flatten().astype(np.int64),
                       minlength=send).astype(np.int64)
    return counts, sums


def main(args=sys.argv[1:]):
    args = parse_args(args)
    levels = args.level
    while len(levels) < len(args.output):
        levels.append(7)
    alignment = json.load(open(args.alignment))
    warper = Warper(alignment["moving"], alignment["reference"])
    segmentation = tifffile.imread(args.reference_segmentation)\
        .astype(np.uint16)
    sm_segmentation = SharedMemory(segmentation.shape,
                                   segmentation.dtype)
    with sm_segmentation.txn() as m:
        m[:] = segmentation
    files = sorted(glob.glob(args.input))
    if len(files) == 0:
        raise IOError("Failed to find any files matching %s" % args.input)
    total_counts = np.zeros(np.max(segmentation) + 1, np.int64)
    total_sums = np.zeros(np.max(segmentation) + 1, np.int64)
    if args.n_cores == 1:
        for z, filename in tqdm.tqdm(enumerate(files), total=len(files)):
            c, s = do_plane(filename, z, sm_segmentation, warper,
                            shrink=args.shrink, grid_size=args.grid_size)
            total_counts += c
            total_sums += s
    else:
        with multiprocessing.Pool(args.n_cores) as pool:
            futures = []
            for z, filename in enumerate(files):
                future = pool.apply_async(
                    do_plane,
                    (filename, z, sm_segmentation, warper, args.shrink,
                     args.grid_size))
                futures.append(future)

            for future in tqdm.tqdm(futures):
                c, s = future.get()
                total_counts += c
                total_sums += s

    with open(args.brain_regions_csv) as fd:
        br = BrainRegions.parse(fd)

    seg_ids = np.where(total_counts > 0)[0]
    counts_per_id = total_counts[seg_ids]
    total_intensities_per_id = total_sums[seg_ids]
    mean_intensity_per_id = \
        total_intensities_per_id.astype(float) / counts_per_id
    for level, output in zip(levels, args.output):
        if level == 7:
            with open(output, "w") as fd:
                fd.write(
                    '"id","region","area","total_intensity","mean_intensity"\n')
                for seg_id, count, total_intensity, mean_intensity in zip(
                        seg_ids, counts_per_id, total_intensities_per_id,
                        mean_intensity_per_id):
                    if seg_id == 0:
                        region = "not in any region"
                    else:
                        region = br.name_per_id.get(seg_id, "id%d" % seg_id)
                    fd.write('%d,"%s",%d, %d, %.2f\n' %
                             (seg_id, region, count, total_intensity,
                              mean_intensity))
        else:
            d = {}
            for seg_id, count, intensity in zip(
                    seg_ids, counts_per_id, total_intensities_per_id):
                try:
                    l = br.get_level_name(seg_id, level)
                except KeyError:
                    l = "region_%d" % seg_id
                if l in d:
                    d[l][0] += count
                    d[l][1] += intensity
                else:
                    d[l] = [count, intensity]
            with open(output, "w") as fd:
                fd.write('"region","area","total_intensity","mean_intensity"\n')
                for l in sorted(d):
                    fd.write('"%s",%d,%d,%.2f\n' %
                             (l, d[l][0], d[l][1],
                              d[l][1] / d[l][0]))


if __name__=="__main__":
    main()
