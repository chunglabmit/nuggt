"""display_image - a quick utility to display an image in Neuroglancer


"""

import argparse
import numpy as np
import tifffile
import neuroglancer
import time
import webbrowser
from nuggt.utils.ngutils import \
    layer, gray_shader, red_shader, green_shader, blue_shader, seglayer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files_and_colors", nargs="+",
                        help="File name followed by display name followed by"
                        "\"red\", \"green\", \"blue\" or \"gray\".")
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
                        help="The URL of the static content source, e.g. "
                        "http://localhost:8080 if being served via npm.")
    args = parser.parse_args()
    if args.static_content_source is not None:
        neuroglancer.set_static_content_source(url=args.static_content_source)
    neuroglancer.set_server_bind_address(args.ip_address, args.port)
    viewer = neuroglancer.Viewer()
    with viewer.txn() as txn:
        for filename, name, colorname in zip(args.files_and_colors[::3],
                                             args.files_and_colors[1::3],
                                             args.files_and_colors[2::3]):
            img = tifffile.imread(filename).astype(np.float32)
            if colorname.lower() == "red":
                shader = red_shader
            elif colorname.lower() == "green":
                shader = green_shader
            elif colorname.lower() == "blue":
                shader = blue_shader
            else:
                shader = gray_shader
            layer(txn, name, img, shader, 1.0)
        if args.segmentation != None:
            seg = tifffile.imread(args.segmentation).astype(np.uint32)
            seglayer(txn, "segmentation", seg)

    print(viewer.get_viewer_url())
    webbrowser.open(viewer.get_viewer_url())
    while True:
        time.sleep(5)