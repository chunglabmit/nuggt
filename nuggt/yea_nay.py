"""A single purpose tool to sort into yes/no classes


"""

import argparse
import json
import neuroglancer
from nuggt.utils.ngutils import *
import tifffile
import threading
import webbrowser


class NuggtYeaNay:

    def __init__(self, imgs, points, quit_cb):
        """Initializer


        :param imgs: a sequence of three-tuples: image, name, shader. The
        possible shaders are nuggt.utils.ngutils.{gray, red, green, blue}_shader

        :param points: an Nx3 array of points where points[:, 0] is the z
        coordinate, points[:, 1] is the y coordinate and points[:, 2] is the
        x coordinate

        :param quit_cb: a function to be called when quitting.
        """
        self.idx = 0
        self.points = points
        self.quit_cb = quit_cb
        self.viewer = neuroglancer.Viewer()
        self._yea = np.zeros(len(points), bool)
        self._nay = np.zeros(len(points), bool)
        with self.viewer.txn() as txn:
            for img, name, shader in imgs:
                layer(txn, name, img.astype(np.float32), shader, 1.0)
        self.display_points()
        self.go_to()
        self.viewer.actions.add("quit", self.on_quit)
        self.viewer.actions.add("yea", self.on_yea)
        self.viewer.actions.add("nay", self.on_nay)
        self.viewer.actions.add("next", self.on_next)
        self.viewer.actions.add("previous", self.on_previous)
        with self.viewer.config_state.txn() as s:
            v = s.input_event_bindings.viewer
            v["control+keyq"] = "quit"
            v["shift+keyy"] = "yea"
            v["shift+keyn"] = "nay"
            v["shift+bracketleft"] = "previous"
            v["shift+bracketright"] = "next"

    @property
    def yea(self):
        """The points annotated as "yea" """
        return self.points[self._yea]

    @property
    def nay(self):
        """The points annotated as "nay" """
        return self.points[self._nay]

    def on_quit(self, s):
        self.quit_cb()

    def on_yea(self, s):
        self._nay[self.idx] = False
        self._yea[self.idx] = True
        self.idx = (self.idx + 1) % len(self.points)
        self.display_points()
        self.go_to()

    def on_nay(self, s):
        self._nay[self.idx] = True
        self._yea[self.idx] = False
        self.idx = (self.idx + 1) % len(self.points)
        self.display_points()
        self.go_to()

    def on_next(self, s):
        self.idx = (self.idx + 1) % len(self.points)
        self.go_to()

    def on_previous(self, s):
        self.idx = (self.idx + len(self.points) - 1) % len(self.points)
        self.go_to()

    def _get_masked_points(self, mask):
        """Return the masked points, in x, y, z form"""
        mp = self.points[mask]
        return mp[:, 2], mp[:, 1], mp[:, 0]

    def display_points(self):
        with self.viewer.txn() as txn:
            pointlayer(txn, "unmarked",
                       *self._get_masked_points(~(self._yea | self._nay)),
                       color="yellow")
            pointlayer(txn, "yea", *self._get_masked_points(self._yea),
                       color="green")
            pointlayer(txn, "nay", *self._get_masked_points(self._nay),
                       color="red")

    def go_to(self):
        with self.viewer.txn() as txn:
            txn.position.voxel_coordinates = self.points[self.idx, ::-1]


def sort_points(imgs, points, launch_ui=False):
    """Sort points into "yea" and "nay" using a Neuroglancer UI

    Note: this prints the URL in the console. You can preconfigure Neuroglancer
    with a specific host and port using neuroglancer.set_server_bind_address.

    This function does not return until the user presses ctrl-Q in the browser.

    You may want to call "neuroglancer.stop()" to recover resources if you
    are repeatedly calling sort_points.

    :param imgs: A sequence of 3-tuples of Numpy 3D array image, its name and
    the shader to use (gray_shader, red_shader, green_shader or blue_shader or
    a custom one of your own)
    :param points: An Nx3 array of points in X, Y, Z order (call with
    points[:, ::-1] to reverse from Z, Y, X).
    :param launch_ui: Launch the UI in a browser if true, launch in a new
    window if launch_ui == "new"
    :return: a two-tuple of "yea" points and "nay" points as selected by
    the user. These are in X, Y, Z order, to reverse, yea[:, ::-1]
    """

    e = threading.Event()
    viewer = NuggtYeaNay(imgs, points, e.set)
    print(viewer.viewer.get_viewer_url())
    if launch_ui == "new":
        webbrowser.open_new(viewer.viewer.get_viewer_url())
    elif launch_ui:
        webbrowser.open(viewer.viewer.get_viewer_url())

    e.wait()
    return viewer.yea, viewer.nay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind-address",
                        help="The IP address to bind to as a webserver. "
                        "The default is 127.0.0.1 which is constrained to "
                        "the local machine.",
                        default="127.0.0.1")
    parser.add_argument("--port", type=int, help="HTTP port for server",
                        default=0)
    parser.add_argument("--gray-image",
                        help="Path to an image file to be displayed in gray.")
    parser.add_argument("--gray-image-name",
                        help="The name of the gray image",
                        default="image")
    parser.add_argument("--red-image",
                        help="Path to an image file to be displayed in red.")
    parser.add_argument("--red-image-name",
                        help="The name of the red image",
                        default="red")
    parser.add_argument("--green-image",
                        help="Path to an image file to be displayed in green.")
    parser.add_argument("--green-image-name",
                        help="The name of the green image",
                        default="green")
    parser.add_argument("--blue-image",
                        help="Path to an image file to be displayed in blue.")
    parser.add_argument("--blue-image-name",
                        help="The name of the blue image",
                        default="blue")
    parser.add_argument("--input-coordinates",
                        help="A JSON file of input coordinates as a list of "
                        "three-tuples in X, Y, Z order",
                        required=True)
    parser.add_argument("--yea-coordinates",
                        help="The name of a JSON file to be written with "
                        "the coordinates of \"yea\" points.")
    parser.add_argument("--nay-coordinates",
                        help="The name of a JSON file to be written with the "
                        "coordinates of \"nay\" points.")
    parser.add_argument("--no-browser",
                        help="Do not launch the browser",
                        action="store_true")
    parser.add_argument("--new-browser-window",
                        help="Open Neuroglancer in a new browser window.",
                        action="store_true")
    args = parser.parse_args()
    neuroglancer.set_server_bind_address(args.bind_address, bind_port=args.port)

    with open(args.input_coordinates) as fd:
        points = np.array(json.load(fd))

    imgs = []
    for path, name, shader in (
            (args.gray_image, args.gray_image_name, gray_shader),
            (args.red_image, args.red_image_name, red_shader),
            (args.green_image, args.green_image_name, green_shader),
            (args.blue_image, args.blue_image_name, blue_shader)):
        if path is not None:
            img = tifffile.imread(path)
            imgs.append((img, name, shader))
    if args.no_browser:
        yea, nay = sort_points(imgs, points)
    elif args.new_browser_window:
        yea, nay = sort_points(imgs, points, launch_ui="new")
    else:
        yea, nay = sort_points(imgs, points, launch_ui=True)
    if args.yea_coordinates is not None:
        yea = yea.astype(points.dtype)
        with open(args.yea_coordinates, "w") as fd:
            json.dump(yea.tolist(), fd)
    if args.nay_coordinates is not None:
        nay = nay.astype(points.dtype)
        with open(args.nay_coordinates, "w") as fd:
            json.dump(nay.tolist(), fd)


if __name__ == "__main__":
    main()