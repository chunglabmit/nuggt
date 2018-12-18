import argparse
import json
import math
import sys


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        required=True,
                        help="The path to the .json input coordinates.")
    parser.add_argument("--output",
                        required=True,
                        help="The path to the .json output coordinates file"
                        " to be written")
    parser.add_argument("--x0",
                        type=float,
                        default=0,
                        help="The leftmost edge of the crop region")
    parser.add_argument("--x1",
                        type=float,
                        default=math.inf,
                        help="The rightmost edge of the crop region")
    parser.add_argument("--y0",
                        type=float,
                        default=0,
                        help="The top edge of the crop region")
    parser.add_argument("--y1",
                        type=float,
                        default=math.inf,
                        help="The bottom edge of the crop region")
    parser.add_argument("--z0",
                        type=float,
                        default=0,
                        help="The shallow edge of the crop region")
    parser.add_argument("--z1",
                        type=float,
                        default=math.inf,
                        help="The deep edge of the crop region")
    return parser.parse_args(args)


def main(args=sys.argv[1:]):
    args = parse_args(args=args)
    points = []
    with open(args.input, "r") as fd:
        for x, y, z in json.load(fd):
            if x >= args.x0 and x < args.x1 and \
               y >= args.y0 and y < args.y1 and \
               z >= args.z0 and z < args.z1:
                points.append((x, y, z))
    with open(args.output, "w") as fd:
        json.dump(points, fd)


if __name__ == "__main__":
    main()
