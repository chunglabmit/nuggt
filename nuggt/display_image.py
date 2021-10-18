"""display_image - a quick utility to display an image in Neuroglancer


"""


import argparse
import glob
import json
import numpy as np
import tifffile
import neuroglancer
import sys
import time
import webbrowser
from nuggt.utils.ngutils import \
    gray_shader, red_shader, green_shader, blue_shader, jet_shader, \
    cubehelix_shader, \
    layer, seglayer, pointlayer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files_and_colors", nargs="+",
                        help="File name followed by display name followed by"
                        "\"red\", \"green\", \"blue\", \"gray\", "
                        "\"jet\" or \"cubehelix\".")
    parser.add_argument("--segmentation",
                        default=None,
                        help="Segmentation volume to display")
    parser.add_argument("--ip-address",
                        default="127.0.0.1",
                        help="IP address of neuroglancer server.")
    parser.add_argument("--port",
                        default=0,
                        type=int,
                        help="Port # of neuroglancer server.")
    parser.add_argument("--static-content-source",
                        default=None,
                        help="Obsolete - no longer has any effect")
    parser.add_argument("--points",
                        help="A points file in Z, Y, X order to display")
    parser.add_argument("--show-n",
                        type=int,
                        help="Show only a certain number of randomly selected "
                        "points.")
    args = parser.parse_args()
    if args.static_content_source is not None:
        print("Warning - --static-content-source no longer has any effect",
              file=sys.stderr)
        print("          You can safely omit this from your command line",
              file=sys.stderr)
    neuroglancer.set_server_bind_address(args.ip_address, args.port)

    # Define default dimensions for the viewer
    dim_names = ["xyzct"[d] for d in range(3)]
    dim_units = ["µm"] * 3
    dim_scales = [1.0] * 3

    default_dimensions = neuroglancer.CoordinateSpace(
        names=dim_names,
        units=dim_units,
        scales=dim_scales)

    viewer = neuroglancer.Viewer()
    with viewer.txn() as txn:
        txn.dimensions = default_dimensions
        for filename, name, colorname in zip(args.files_and_colors[::3],
                                             args.files_and_colors[1::3],
                                             args.files_and_colors[2::3]):
            if colorname.lower() == "red":
                shader = red_shader
            elif colorname.lower() == "green":
                shader = green_shader
            elif colorname.lower() == "blue":
                shader = blue_shader
            elif colorname.lower() in ("gray", "grey"):
                shader = gray_shader
            elif colorname.lower() == "jet":
                shader = jet_shader
            else:
                shader = cubehelix_shader
            if filename.startswith("precomputed://"):
                txn.layers[name] = neuroglancer.ImageLayer(
                    source = filename,
                    shader = shader % 1.0
                )
                continue
            paths = sorted(glob.glob(filename))
            if len(paths) == 0:
                sys.stderr.write("Could not find any files named %s" % filename)
                exit(1)
            elif len(paths) == 1:
                img = tifffile.imread(paths[0])
            else:
                img = np.array([tifffile.imread(_) for _ in paths])
            layer(txn, name, img, shader, 1.0, dimensions=default_dimensions)
        if args.segmentation != None:
            seg = tifffile.imread(args.segmentation).astype(np.uint32)
            seglayer(txn, "segmentation", seg)
        if args.points is not None:
            with open(args.points) as fd:
                points = np.array(json.load(fd))
                if args.show_n is not None:
                    points = points[np.random.choice(len(points), args.show_n)]
                pointlayer(txn, "points",
                           points[:, 0], points[:, 1], points[:, 2], "red")

    print(viewer.get_viewer_url())
    #webbrowser.open(viewer.get_viewer_url())
    while True:
        time.sleep(5)


if __name__=="__main__":
    main()
