"""rescale_alignment_file - change the scale of (and flip) points

Typically, a stack to be aligned will be reduced in size and flipped to
prepare it for alignment. This takes the alignment output and undoes the
flipping and rescales the points to the correct size.
"""

import argparse
import glob
import numpy as np
import json
import sys
import tifffile

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        help="The alignment points dictionary file as produced"
                        " by nuggt-align or make-alignment-file.",
                        required=True)
    parser.add_argument("--alignment-image",
                        help="The reduced-size image that was aligned",
                        required=True)
    parser.add_argument("--stack",
                        help="A glob expression that selects the files in the "
                        "stack of the full-size image, e.g. /path/to/*.tiff",
                        required=True)
    parser.add_argument("--output",
                        help="The path name of the json file to be written",
                        required=True)
    parser.add_argument("--x-index",
                        help="The index of the x-coordinate in the alignment"
                             " points matrix, e.g. \"0\" if the x and z "
                        "axes were transposed. Defaults to 2.",
                        type=int,
                        default=2)
    parser.add_argument("--y-index",
                        help="The index of the y-coordinate in the alignment"
                             " points matrix, e.g. \"0\" if the y and z "
                        "axes were transposed. Defaults to 1.",
                        type=int,
                        default=1)
    parser.add_argument("--z-index",
                        help="The index of the z-coordinate in the alignment"
                             " points matrix, e.g. \"2\" if the x and z "
                        "axes were transposed. Defaults to 0.",
                        type=int,
                        default=0)
    parser.add_argument("--flip-x",
                        help="Indicates that the image should be flipped "
                        "in the X direction after transposing and resizing.",
                        action="store_true",
                        default=False)
    parser.add_argument("--flip-y",
                        help="Indicates that the image should be flipped "
                        "in the y direction after transposing and resizing.",
                        action="store_true",
                        default=False)
    parser.add_argument("--flip-z",
                        help="Indicates that the image should be flipped "
                        "in the z direction after transposing and resizing.",
                        action="store_true",
                        default=False)
    parser.add_argument("--clip-x",
                        help="The clipping region that was applied to the "
                        "original stack in the X direction. This should be "
                        "in the format, \"<xmin>-<xmax>\" where <xmin> and "
                        "<xmax> are integers")
    parser.add_argument("--clip-y",
                        help="The clipping region that was applied to the "
                        "original stack in the Y direction. This should be "
                        "in the format, \"<ymin>-<ymax>\" where <ymin> and "
                        "<ymax> are integers")
    parser.add_argument("--clip-z",
                        help="The clipping region that was applied to the "
                        "original stack in the Z direction. This should be "
                        "in the format, \"<zmin>-<zmax>\" where <zmin> and "
                        "<zmax> are integers")
    return parser.parse_args(args)

def transform(points, alignment_shape, stack_shape,
              xidx, yidx, zidx, flipx, flipy, flipz):
    """Transform the points from the alignment frame to the stack frame

    :param points: the points in the alignment space
    :param alignment_shape: the shape of the alignment image
    :param stack_shape: the shape of the equivalent stack image
    :param xidx: the index of the x coordinate in the points, (0, 1 or 2)
    :param yidx: the index of the y coordinate in the points, (0, 1 or 2)
    :param zidx: the index of the z coordinate in the points, (0, 1 or 2)
    :param flipx: True if the image was initially flipped in the X direction
    :param flipy: True if the image was initially flipped in the Y direction
    :param flipz: True if the image was initially flipped in the Z direction
    :return: the transformed points
    """
    points = np.atleast_2d(points)
    zc = points[:, zidx] * stack_shape[0] / alignment_shape[zidx]
    if flipz:
        zc = stack_shape[0] - 1 - zc
    yc = points[:, yidx] * stack_shape[1] / alignment_shape[yidx]
    if flipy:
        yc = stack_shape[1] - 1 - yc
    xc = points[:, xidx] * stack_shape[2] / alignment_shape[xidx]
    if flipx:
        xc = stack_shape[2] - 1 - xc
    return np.column_stack((zc, yc, xc))


def main():
    args = parse_args()
    stackfiles = sorted(glob.glob(args.stack))
    y_extent, x_extent = tifffile.imread(stackfiles[0]).shape
    z_extent = len(stackfiles)
    stack_shape = [z_extent, y_extent, x_extent]
    if args.clip_x is not None:
        xmin, xmax = [int(_) for _ in args.clip_x.split(",")]
        stack_shape[2] = xmax - xmin
    else:
        xmin = 0
        xmax = x_extent
    if args.clip_y is not None:
        ymin, ymax = [int(_) for _ in args.clip_y.split(",")]
        stack_shape[1] = ymax - ymin
    else:
        ymin = 0
        ymax = y_extent
    if args.clip_z is not None:
        zmin, zmax = [int(_) for _ in args.clip_z.split(",")]
        stack_shape[0] = zmax - zmin
    else:
        zmin = 0
        zmax = z_extent
    alignment_shape = tifffile.imread(args.alignment_image).shape
    with open(args.input) as fd:
        d = json.load(fd)
    points = np.array(d["moving"])
    xform = transform(points,
                      alignment_shape=alignment_shape,
                      stack_shape=stack_shape,
                      xidx=args.x_index,
                      yidx=args.y_index,
                      zidx=args.z_index,
                      flipx=args.flip_x,
                      flipy=args.flip_y,
                      flipz=args.flip_z)
    xform[:, 0] += zmin
    xform[:, 1] += ymin
    xform[:, 2] += xmin
    d["moving"] = xform.tolist()
    with open(args.output, "w") as fd:
        json.dump(d, fd)

if __name__ == "__main__":
    main()