"""A single purpose tool to sort into yes/no classes


"""

import argparse
import json
import neuroglancer
from nuggt.utils.ngutils import *
import tifffile
import threading
import webbrowser

MSG_INFO = "Info"
MSG_WARNING = "Warning"
MSG_ERROR = "Error"

class NuggtYeaNay:

    def __init__(self, imgs, points, quit_cb, save_cb):
        """Initializer


        :param imgs: a sequence of three-tuples: image, name, shader. The
        possible shaders are nuggt.utils.ngutils.{gray, red, green, blue}_shader

        :param points: an Nx3 array of points where points[:, 0] is the z
        coordinate, points[:, 1] is the y coordinate and points[:, 2] is the
        x coordinate

        :param quit_cb: a function to be called when quitting.
        :param save_cb: a function to be called when saving
        """
        self.idx = 0
        self.points = points
        self.quit_cb = quit_cb
        self.save_cb = save_cb
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
        self.viewer.actions.add("go-to", self.on_go_to)
        self.viewer.actions.add("next", self.on_next)
        self.viewer.actions.add("next-unmarked", self.on_next_unmarked)
        self.viewer.actions.add("previous", self.on_previous)
        self.viewer.actions.add("previous-unmarked", self.on_previous_unmarked)
        self.viewer.actions.add("center", self.on_center)
        if save_cb is not None:
            self.viewer.actions.add("save", self.on_save)
        with self.viewer.config_state.txn() as s:
            v = s.input_event_bindings.viewer
            v["control+keyq"] = "quit"
            v["shift+keyy"] = "yea"
            v["shift+keyn"] = "nay"
            v["shift+keyg"] = "go-to"
            v["shift+bracketleft"] = "previous"
            v["control+bracketleft"] = "previous-unmarked"
            v["shift+bracketright"] = "next"
            v["control+bracketright"] = "next-unmarked"
            v["shift+keyc"] = "center"
            if save_cb is not None:
                v["control+keys"] = "save"

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

    def on_next_unmarked(self, s):
        unmarked_idx = np.where(~ (self._yea | self._nay))[0]
        if len(unmarked_idx) == 0:
            with self.viewer.config_state.txn() as txn:
                txn.status_messages[MSG_WARNING] = "No next unmarked point"
            return
        larger = unmarked_idx[unmarked_idx > self.idx]
        if len(larger) > 0:
            self.idx = larger[0]
        else:
            self.idx = unmarked_idx[0]
        self.go_to()

    def on_previous(self, s):
        self.idx = (self.idx + len(self.points) - 1) % len(self.points)
        self.go_to()

    def on_previous_unmarked(self, s):
        unmarked_idx = np.where(~ (self._yea | self._nay))[0]
        if len(unmarked_idx) == 0:
            with self.viewer.config_state.txn() as txn:
                txn.status_messages[MSG_WARNING] = "No previous unmarked point"
            return
        smaller = unmarked_idx[unmarked_idx < self.idx]
        if len(smaller) > 0:
            self.idx = smaller[-1]
        else:
            self.idx = unmarked_idx[-1]
        self.go_to()

    def on_go_to(self, s):
        for layer_name in ("unmarked", "yea", "nay"):
            layer = s.viewerState.layers[layer_name].layer
            d = layer.to_json()
            if "selectedAnnotation" in d:
                idx = int(d["selectedAnnotation"])
                if layer_name == "unmarked":
                    mask = ~ (self._yea | self._nay)
                elif layer_name == "yea":
                    mask = self._yea
                else:
                    mask = self._nay
                self.idx = np.where(mask)[0][idx]
                self.go_to()
                break
        else:
            with self.viewer.config_state.txn() as txn:
                txn.status_messages[MSG_WARNING] = "No selected point"


    def on_center(self, s):
        self.go_to()

    def on_save(self, s):
        try:
            self.save_cb(self.yea, self.nay)
            with self.viewer.config_state.txn() as txn:
                txn.status_messages[MSG_INFO] = "Yea and Nay saved"
        except BaseException as e:
            with self.viewer.config_state.txn() as txn:
                txn.status_message[MSG_ERROR] = str(e)

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


def sort_points(imgs, points, launch_ui=False, save_cb=None):
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
    viewer = NuggtYeaNay(imgs, points, e.set,
                         save_cb=save_cb)
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
    parser.add_argument("--xyz",
                        action="store_true",
                        help="Points are stored in x, y, z order")
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
    parser.add_argument("--static-content-source",
                        default=None,
                        help="The URL of the static content source, e.g. "
                        "http://localhost:8080 if being served via npm.")

    args = parser.parse_args()
    if args.static_content_source != None:
        neuroglancer.set_static_content_source(url=args.static_content_source)
    neuroglancer.set_server_bind_address(args.bind_address, bind_port=args.port)

    with open(args.input_coordinates) as fd:
        points = np.array(json.load(fd))
    if args.xyz:
        points = points[:, ::-1]

    imgs = []
    for path, name, shader in (
            (args.gray_image, args.gray_image_name, gray_shader),
            (args.red_image, args.red_image_name, red_shader),
            (args.green_image, args.green_image_name, green_shader),
            (args.blue_image, args.blue_image_name, blue_shader)):
        if path is not None:
            img = tifffile.imread(path)
            imgs.append((img, name, shader))

    def save_cb(yea, nay):
        if args.yea_coordinates is not None:
            yea = yea.astype(points.dtype)
            if args.xyz:
                yea = yea[:, ::-1]
            with open(args.yea_coordinates, "w") as fd:
                json.dump(yea.tolist(), fd)
        if args.nay_coordinates is not None:
            nay = nay.astype(points.dtype)
            if args.xyz:
                nay = nay[:, ::-1]
            with open(args.nay_coordinates, "w") as fd:
                json.dump(nay.tolist(), fd)

    if args.no_browser:
        yea, nay = sort_points(imgs, points, save_cb=save_cb)
    elif args.new_browser_window:
        yea, nay = sort_points(imgs, points, launch_ui="new",
                               save_cb=save_cb)
    else:
        yea, nay = sort_points(imgs, points, launch_ui=True,
                               save_cb=save_cb)
    save_cb(yea, nay)

if __name__ == "__main__":
    main()