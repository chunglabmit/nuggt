"""rescale_image_for_alignment: create a downsampled image for atlas alignment

The image to be aligned should be rescaled and rotated to approximately match
the atlas image before running sitk-align. This utility provides cropping,
rotating and rescaling of an image stack to generate a suitable image.
"""

import argparse
import glob
import multiprocessing
import numpy as np
from scipy.ndimage import zoom
import sys
import tifffile
import tqdm

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        required=True,
                        help="The input glob expression for the image stack")
    parser.add_argument("--output",
                        required=True,
                        help="The name of the .tif file to be output")
    parser.add_argument("--atlas-file",
                        required=True,
                        help="The path to the atlas image .tif file")
    parser.add_argument("--x-index",
                        help="The index of the x-coordinate output"
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
                        help="Clip the image stack in the X direction to "
                        "the coordinates given here. The format is "
                        "--clip-x=<min-x>,<max-x>")
    parser.add_argument("--clip-y",
                        help="Clip the image stack in the Y direction to "
                        "the coordinates given here. The format is "
                        "--clip-y=<min-y>,<max-y>")
    parser.add_argument("--clip-z",
                        help="Clip the image stack in the Z direction to "
                        "the coordinates given here. The format is "
                        "--clip-z=<min-z>,<max-z>")
    parser.add_argument("--thread-count",
                        type=int,
                        default=6,
                        help="# of threads used to read images in parallel")
    return parser.parse_args(args)


def read_one(filename, x_min, x_max, y_min, y_max, x_scale, y_scale):
    """Read one plane

    :param filename: the .tif file to read
    :param x_min: start of clipping region in the X direction
    :param x_max: end of clipping region in the X direction
    :param y_min: start of clipping region in the Y direction
    :param y_max: end of clipping region in the Y direction
    :param x_scale: shrink the clipping region in the x direction by this frac
    :param y_scale: shrink the clipping region in the y direction by this frac
    :return: the plane after clipping and scaling
    """
    plane = tifffile.imread(filename)[y_min:y_max, x_min:x_max]
    return zoom(plane, (y_scale, x_scale))


def main(args=sys.argv[1:]):
    params = parse_args(args)
    stack_files = sorted(glob.glob(params.input))
    if len(stack_files) == 0:
        sys.stderr.write(
            "Unable to find any image files matching the pattern, \"%s\".\n" %
            params.input)
        exit(1)
    try:
        atlas_file = tifffile.imread(params.atlas_file)
    except FileNotFoundError:
        sys.stderr.write("Could not find the atlas file, \"%s\".\n"
                         % params.atlas_file)
        exit(1)
    img0 = tifffile.imread(stack_files[0])
    if params.clip_x is None:
        x_min = 0
        x_max = img0.shape[1]
    else:
        x_min, x_max = [int(_) for _ in params.clip_x.split(",")]
    if params.clip_y is None:
        y_min = 0
        y_max = img0.shape[0]
    else:
        y_min, y_max = [int(_) for _ in params.clip_y.split(",")]
    if params.clip_z is None:
        z_min = 0
        z_max = len(stack_files)
    else:
        z_min, z_max = [int(_) for _ in params.clip_z.split(",")]
    x_index = params.x_index
    y_index = params.y_index
    z_index = params.z_index
    scale_x = atlas_file.shape[x_index] / (x_max - x_min)
    scale_y = atlas_file.shape[y_index] / (y_max - y_min)
    stack = []
    with multiprocessing.Pool(params.thread_count) as pool:
        futures = []
        for z in np.linspace(z_min, z_max-1, atlas_file.shape[z_index]):
            if np.floor(z) == np.ceil(z):
                future = pool.apply_async(
                    read_one,
                    (stack_files[int(z)],
                     x_min, x_max,
                     y_min, y_max,
                     scale_x, scale_y)
                )
                futures.append((future, future, .5))
            else:
                future1 = pool.apply_async(
                    read_one,
                    (stack_files[int(np.floor(z))],
                     x_min, x_max,
                     y_min, y_max,
                     scale_x, scale_y))
                future2 = pool.apply_async(
                    read_one,
                    (stack_files[int(np.ceil(z))],
                     x_min, x_max,
                     y_min, y_max,
                     scale_x, scale_y))
                futures.append((future1, future2, 1 - (z - np.floor(z))))
        for future1, future2, frac in tqdm.tqdm(futures):
            p1 = future1.get()
            p2 = future2.get()
            plane = p1.astype(np.float32) * frac +\
                    p2.astype(np.float32) * (1 - frac)
            stack.append(plane.astype(p1.dtype))
    img = np.array(stack).transpose(z_index, y_index, x_index)
    if params.flip_x:
        img = img[..., ::-1]
    if params.flip_y:
        img = img[:, ::-1]
    if params.flip_z:
        img = img[::-1]
    tifffile.imsave(params.output, img)


if __name__ == "__main__":
    main()


