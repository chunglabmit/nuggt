import argparse
import glob
import json
import multiprocessing
import numpy as np
import os
from scipy.ndimage import map_coordinates
import sys
import tifffile
import tqdm

from .utils.warp import Warper

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Convert a segmentation in the reference space\n"
        "to a segmentation in the sample's space.")
    parser.add_argument(
        "--input",
        help="The input segmentation, a .tiff file",
        required=True
    )
    parser.add_argument(
        "--alignment",
        help="An alignment where the reference list of points is in the "
        "same reference frame as the input and whose moving list of points is "
        "in the same reference frame as the desired output",
        required=True
    )
    parser.add_argument(
        "--output",
        help="The directory for the output file. Files will be written as "
        "image_xxxx.tiff",
        required=True
    )
    parser.add_argument(
        "--stack",
        help="A stack similarly shaped to the desired output. This should "
        "be in the format of a glob expression, e.g. \"/path/to/*.tiff\".",
        required=True
    )
    parser.add_argument(
        "--n-cores",
        help="The number of CPUs to use to process the data.",
        default=os.cpu_count(),
        type=int
    )
    parser.add_argument(
        "--downsample-factor",
        help="Downsample the image by this factor with respect to the output "
        "stack size and alignment.",
        default=1.0,
        type=float
    )
    parser.add_argument(
        "--grid-spacing",
        help="The number of voxels between nodes in the output space "
             "for the cuboid approximation spline",
        default=100,
        type=int
    )
    parser.add_argument(
        "--silent",
        help="Don't display the progress bar",
        action="store_true"
    )
    parser.add_argument(
        "--compress",
        help="The TIFF compression level: 0-9",
        type=int,
        default=3
    )
    return parser.parse_args()


"""The global segmentation goes here."""
SEG = None


"""The global coordinate warper goes here.

The warper converts coordinates in the output space to that of the segmentation
"""
WARPER = None


def make_warper(alignment, downsample_factor, grid_spacing, output_shape):
    """
    Make the global warper for translating between the reference and moving
    frames of reference.

    :param alignment: the json alignment structure
    :param downsample_factor: How much to downsample the moving coordinates
    :param grid_spacing: the grid spacing of the approximator
    :param output_shape: the shape of the output volume
    :return:
    """
    global WARPER
    ze, ye, xe = [int(np.ceil(_ / grid_spacing)) * grid_spacing
                  for _ in output_shape]
    xa, ya, za = [np.arange(0, _, grid_spacing)
                  for _ in (xe, ye, ze)]
    src = [(x / downsample_factor,
            y / downsample_factor,
            z / downsample_factor)
           for x, y, z in alignment["moving"]]
    dest = alignment["reference"]
    warper = Warper(src, dest)
    approximator = warper.approximate(za, ya, xa)
    WARPER = approximator


def get_stack_dimensions(stack, downsample_factor):
    """
    Compute the stack dimensions from the number of images in the stack and
    the size of the first one.
    :param stack: a glob expression for the stack's files
    :param downsample_factor: How much to downsample the stack size
    :return: the dimensions of the output stack
    """
    stack_files = glob.glob(stack)
    if len(stack_files) == 1:
        z, y, x = tifffile.imread(stack_files[0]).shape
    else:
        z = len(stack_files)
        y, x = tifffile.imread(stack_files[0]).shape[:2]
    return np.array([int(np.ceil(_/ downsample_factor)) for _ in (z, y, x)])


def write_one_z(z, dim, path, compress):
    y, x = np.mgrid[0:dim[0], 0:dim[1]]
    zz = np.ones(dim, int) * z
    zf, yf, xf = [_.flatten() for _ in (zz, y, x)]
    batch_size = 10000
    rx, ry, rz = [ [] for _ in range(3)]
    for i0 in range(0, np.prod(dim), batch_size):
        i1 = min(np.prod(dim), i0+batch_size)
        rzi, ryi, rxi = \
            WARPER(np.column_stack((zf[i0:i1], yf[i0:i1], xf[i0:i1])))\
                .transpose()
        rx.append(rxi)
        ry.append(ryi)
        rz.append(rzi)
    rx, ry, rz = [np.hstack(_) for _ in (rx, ry, rz)]
    # Make NaN into out-of-bounds so they get set to zero
    rx[np.isnan(rx)] = -1
    ry[np.isnan(ry)] = -1
    rz[np.isnan(rz)] = -1
    rx, ry, rz = [np.round(_.reshape(dim)).astype(np.int32)
                  for _ in (rx, ry, rz)]
    img = map_coordinates(SEG, [rz, ry, rx], order=0, cval=0).astype(SEG.dtype)
    tifffile.imsave(path, img, compress=compress)


def write_output(output, output_dim, silent, n_cores, compress):
    """
    Write the output stack

    :param seg: the segmentation
    :param output: The output directory
    :param output_dim: The dimensions of the output stack
    :param silent: if True, don't display the progress bar
    :param n_cores: # of worker processes to use
    :param compress: the TIFF compression level
    """
    with multiprocessing.Pool(n_cores) as pool:
        futures = []
        for z in range(0, output_dim[0]):
            path = os.path.join(output, "img_%04d.tiff" % z)
            futures.append(pool.apply_async(
                write_one_z,
                (z, output_dim[1:], path, compress)
            ))
        for future in tqdm.tqdm(futures, disable=silent):
            future.get()


def main(argv=sys.argv[1:]):
    global SEG
    args = parse_args(argv)
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    SEG = tifffile.imread(args.input)
    with open(args.alignment) as fd:
        alignment = json.load(fd)
    output_dim = get_stack_dimensions(args.stack, args.downsample_factor)
    make_warper(alignment, args.downsample_factor, args.grid_spacing,
                output_dim)
    write_output(args.output, output_dim, args.silent, args.n_cores,
                 args.compress)


if __name__=="__main__":
    main()