"""make_alignment_file - a script for making the --points file for nuggt-align

Given a transformation from the reference frame to the target frame, generate
the --points file for nuggt-align containing the correspondences.
"""

import argparse
import json
import SimpleITK as sitk
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from .sitk_align import transform
import sys

def parse_args(args=sys.argv[1:]):
    """Parse the arguments for the make_alignment_file script

    :param args: sys.argv[1:] or similar
    :return: the output of argparse.ArgumentParser().parse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-points",
                        help="A json file containing the points to be "
                        "transformed from the reference frame to the moving "
                        "frame.",
                        required=True)
    parser.add_argument("--moving-image",
                        help="The path to the movingimage, a 3D .tif file",
                        required=True)
    parser.add_argument("--output",
                        help="The name of the output file.",
                        required=True)
    parser.add_argument("transform_parameters", nargs="+",
                        help="TransformParameters.txt files to be loaded.")
    parser.add_argument("--xyz",
                        help="Coordinates in --reference-points file are in "
                        "X, Y, Z form, not Z, Y, X",
                        action="store_true",
                        default=False)
    parser.add_argument("--reference-key",
                        help="The key for the reference points in the json "
                        "file.",
                        default="reference")
    parser.add_argument("--moving-key",
                        help="The key for the moving points in the json "
                        "file.",
                        default="moving")
    return parser.parse_args(args)


def main():
    args = parse_args()
    sitk_ref_img = sitk.ReadImage(args.moving_image)
    with open(args.reference_points) as fd:
        ref_points = np.array(json.load(fd))
    if args.xyz:
        ref_points = ref_points[:, ::-1]
    vpm = sitk.VectorOfParameterMap()
    for tp_path in args.transform_parameters:
        vpm.append(sitk.ReadParameterFile(tp_path))
    apoints = transform(ref_points, sitk_ref_img, vpm)
    with open(args.output, "w") as fd:
        json.dump({
            args.reference_key:ref_points.tolist(),
            args.moving_key:apoints.tolist()
        }, fd)


if __name__ == "__main__":
    main()