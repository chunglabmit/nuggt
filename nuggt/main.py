import argparse
import json
import multiprocessing
import neuroglancer
import numpy as np
import os
import glob
import sys
import tempfile
import tifffile
import tqdm
import webbrowser
import time

from neuroglancer.server import BaseRequestHandler
from .utils.ngutils import *
from .ngreference import  NGReference

viewer = None
outside_points = []
args = None
x_extent = 0
y_extent = 0
z_extent = 0
width = 0
height = 0
depth = 0

def say(msg, category):
    with viewer.config_state.txn() as txn:
        txn.status_messages[category] = msg


def action_handler(s, min_distance):
    point = s.mouse_voxel_coordinates
    print( dir(s), type(s))
    with viewer.txn() as txn:
        points = [_.point.tolist()
                  for _ in txn.layers["annotation"].annotations]
        if any([np.sqrt(sum([(a - b) ** 2 for a, b in zip(p, point)]))
                < min_distance
                for p in points]):
            say("Point too close to some other point!", "annotation")
            return
        points.append(point.tolist())
        x, y, z = [np.array([_[idx] for _ in points]) for idx in range(3)]
        pointlayer(txn, "annotation", x, y, z, "yellow")
        say("Added point at %.2f, %.2f, %.2f" % (point[0], point[1], point[2]),
            "annotation")


def delete_handler(s, min_distance):
    point = s.mouse_voxel_coordinates
    with viewer.txn() as txn:
        points = [_.point.tolist()
                  for _ in txn.layers["annotation"].annotations]
        if len(points) == 0:
            say("No points to delete", "delete")
            return
        distances = np.sqrt([sum([(a - b) ** 2 for a, b in zip(p, point)])
                             for p in points])
        idx = np.argmin(distances)
        if distances[idx] > min_distance:
            say("Not close enough to any point to delete", "delete")
        else:
            say("Deleting %.2f, %.2f, %.2f" % (points[idx][0],
                                               points[idx][1],
                                               points[idx][2]), "delete")
            points.pop(idx)
            x, y, z = [np.array([_[idx] for _ in points]) for idx in range(3)]
            pointlayer(txn, "annotation", x, y, z, "yellow")


def save(output):
    post_message_immediately(viewer, "save", "Saving annotations... patience")
    points = [_.point.tolist() for
              _ in viewer.state.layers["annotation"].annotations]
    if os.path.exists(output):
        mtime = os.stat(output).st_mtime
        ext = time.strftime('.%Y-%m-%d_%H-%M-%S', time.localtime(mtime))
        os.rename(output, output+ext)
    with open(output, "w") as fd:
        fd.write("[\n")
        need_comma = False
        for x, y, z in outside_points + points:
            if need_comma:
                fd.write(",\n")
            else:
                need_comma = True
            fd.write("  [%.2f,%.2f,%.2f]" % (x, y, z))
        fd.write("\n]\n")
    say("Saved annotations to %s" % output, "save")


def load_one_plane(imgpath, tfpath, x0, x1, y0, y1, z):
    plane: np.ndarray = tifffile.imread(imgpath)[y0:y1, x0:x1]
    height, width = plane.shape
    a = np.memmap(tfpath, dtype=plane.dtype,
                  offset=height * width * z * plane.dtype.itemsize,
                  shape=plane.shape)
    a[:] = plane
    return height, width, plane.dtype


def load_image(path, x0=0, x1=None, y0=0, y1=None, z0=0, z1=None):
    filenames = sorted(glob.glob(path))
    if len(filenames) > 1:
        if sys.prefix.startswith("linux"):
            tempdir = "/dev/shm"
        else:
            tempdir = tempfile.tempdir
        with tempfile.NamedTemporaryFile(
                dir=tempdir,
                prefix="proc_%d_" % os.getpid(),
                suffix=".shm") as tf:
            tfpath = tf.name
            futures = []
            with multiprocessing.Pool(6) as pool:
                for z in range(z0, z1):
                    futures.append(pool.apply_async(
                        load_one_plane,
                        (filenames[z], tfpath, x0, x1, y0, y1, z-z0)))
                for future in tqdm.tqdm(futures):
                    height, width, dtype = future.get()
            result = np.memmap(tfpath,
                               dtype=dtype,
                               shape=(z1-z0, height, width)).copy()
    else:
        result = tifffile.imread(filenames[0])
    return result.astype(np.float32)

LOAD_HTML="""
<html><head><title>Neuroglancer image loader</title></head>
<body>
<h2>Load Neuroglancer volume</h2>
<form method="post">
<div>
<table>
<tr><td>X0</td><td><input type="text" name="x0" value="%(x0)d"/></td>
    <td>X1</td><td><input type="text" name="x1" value="%(x1)d"/></td></tr>
<tr><td>Y0</td><td><input type="text" name="y0" value="%(y0)d"/></td>
    <td>Y1</td><td><input type="text" name="y1" value="%(y1)d"/></td></tr>
<tr><td>Z0</td><td><input type="text" name="z0" value="%(z0)d"/></td>
    <td>Z1</td><td><input type="text" name="z1" value="%(z1)d"/></td></tr>
</div>
<div>
<input type="submit"/>
</div>
</form>
</body>
</html>
"""

x0 = 0
x1 = 0
y0 = 0
y1 = 0
z0 = 0
z1 = 0


def reposition(x0a, x1a, y0a, y1a, z0a, z1a):
    """Reposition the viewer at the given subvolume"""
    global x0, x1, y0, y1, z0, z1
    global viewer
    global outside_points
    global args
    x0, x1, y0, y1, z0, z1 = x0a, x1a, y0a, y1a, z0a, z1a
    img = load_image(args.image, x0, x1, y0, y1, z0, z1)
    if args.alt_image is not None:
        alt_img = load_image(args.alt_image, x0, x1, y0, y1, z0, z1)

    with viewer.txn() as txn:
        points = outside_points + [_.point.tolist()
                                   for _ in txn.layers["annotation"].annotations]
        points, outside_points = filter_points(points)
        layer(txn, "image", img, gray_shader, 1.0, x0, y0, z0)
        if args.alt_image is not None:
            layer(txn, "alt_image", alt_img, green_shader, 1.0,
                  x0, y0, z0)
        x, y, z = [np.array([_[idx] for _ in points]) for idx in range(3)]
        pointlayer(txn, "annotation", x, y, z, "yellow")
        txn.position.voxel_coordinates =\
            ((x0 + x1) / 2, (y0 + y1) / 2, (z0+z1) / 2)


class LoadHandler(BaseRequestHandler):
    def get(self):
        global x0, x1, y0, y1, z0, z1
        self.set_header('Content-type', "text/html")
        self.finish(LOAD_HTML % globals())

    def post(self):
        x0a, x1a, y0a, y1a, z0a, z1a = [
            int(self.get_argument(_)) for _ in
            ("x0", "x1", "y0", "y1", "z0", "z1")
        ]
        reposition(x0a, x1a, y0a, y1a, z0a, z1a)
        self.set_header('Content-type', "text/html")
        self.finish(LOAD_HTML % globals())


def patch_tornado():
    from neuroglancer.server import weakref, concurrent, sockjs
    from neuroglancer.server import SockJSHandler
    from neuroglancer.server import SOCKET_PATH_REGEX_WITHOUT_GROUP
    from neuroglancer.server import tornado, STATIC_PATH_REGEX
    from neuroglancer.server import INFO_PATH_REGEX, DATA_PATH_REGEX
    from neuroglancer.server import SKELETON_PATH_REGEX, MESH_PATH_REGEX
    from neuroglancer.server import StaticPathHandler, VolumeInfoHandler
    from neuroglancer.server import SubvolumeHandler, SkeletonHandler
    from neuroglancer.server import MeshHandler, make_random_token
    from neuroglancer.server import socket, static

    class NGServer(neuroglancer.server.Server):
        def __init__(self, ioloop, bind_address='127.0.0.1', bind_port=0):
            self.viewers = weakref.WeakValueDictionary()
            self.token = make_random_token()
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=multiprocessing.cpu_count())

            self.ioloop = ioloop
            sockjs_router = sockjs.tornado.SockJSRouter(
                SockJSHandler, SOCKET_PATH_REGEX_WITHOUT_GROUP, io_loop=ioloop)
            sockjs_router.neuroglancer_server = self
            app = self.app = tornado.web.Application([
                ("^/load$", LoadHandler, dict(server=self)),
                (STATIC_PATH_REGEX, StaticPathHandler, dict(server=self)),
                (INFO_PATH_REGEX, VolumeInfoHandler, dict(server=self)),
                (DATA_PATH_REGEX, SubvolumeHandler, dict(server=self)),
                (SKELETON_PATH_REGEX, SkeletonHandler, dict(server=self)),
                (MESH_PATH_REGEX, MeshHandler, dict(server=self)),
            ] + sockjs_router.urls)
            http_server = tornado.httpserver.HTTPServer(app)
            sockets = tornado.netutil.bind_sockets(port=bind_port, address=bind_address)
            http_server.add_sockets(sockets)
            actual_port = sockets[0].getsockname()[1]

            if neuroglancer.server.global_static_content_source is None:
                neuroglancer.server.global_static_content_source = static.get_default_static_content_source()

            if bind_address == '0.0.0.0':
                hostname = socket.getfqdn()
            else:
                hostname = bind_address

            self.server_url = 'http://%s:%s' % (hostname, actual_port)

    neuroglancer.server.Server = NGServer


def filter_points(points):
    new_points = []
    other_points = []
    for x, y, z in points:
        if x0 <= x < x1 and \
                y0 <= y < y1 and \
                z0 <= z < z1:
            new_points.append((x, y, z))
        else:
            other_points.append((x, y, z))
    return new_points, other_points


class NavViewer(NGReference):

    def bind(self):
        """Bind the nav viewer"""
        self.viewer.actions.add("jump", self.on_action)
        with self.viewer.config_state.txn() as s:
            s.input_event_bindings.viewer["keyj"] = "jump"

    def action_handler(self, s, moving_point):
        post_message_immediately(self.viewer,
                                 "jumping",
                                 "Repositioning viewer...patience")
        x0a = int(max(0, moving_point[2] - width // 2))
        x1a = int(min(x_extent, x0a + width))
        y0a = int(max(0, moving_point[1] - height //2))
        y1a = int(min(y_extent, y0a + height))
        z0a = int(max(0, moving_point[0] - depth // 2))
        z1a = int(min(z_extent, z0a + depth))
        reposition(x0a, x1a, y0a, y1a, z0a, z1a)
        with self.viewer.config_state.txn() as txn:
            txn.status_messages["jumping"] = "Viewer repositioned"


def main():
    global viewer
    global outside_points
    global x0, x1, y0, y1, z0, z1
    global args
    global x_extent, y_extent, z_extent, width, height, depth

    parser = argparse.ArgumentParser(description="NeUroGlancer Ground Truth")
    parser.add_argument("--port", type=int, help="HTTP port for server",
                        default=0)
    parser.add_argument("--image", help="Path to image file", required=True)
    parser.add_argument("--alt-image",
                        help="Path to a second image channel")
    parser.add_argument("--output", help="Path to list of point annotations",
                        required=True)
    parser.add_argument(
        "--detected", help="Path to list of detected point annotations",
        required=False)
    parser.add_argument("--min-distance",
                        help="Minimum distance between two annotations",
                        type=int, default=10)
    parser.add_argument("--segmentation",
                        help="Path to existing segmentation file (optional)",
                        default="")
    parser.add_argument("--coordinates",
                        help="Coordinates of the image volume to edit"
                        "(x0,x1,y0,y1,z0,z1). "
                        "Example: \"1000,2000,4000,5000,300,500\" to edit"
                        "x=1000 to 2000, y=4000 to 5000, z=300 to 500.")
    parser.add_argument("--bind-address",
                        help="The IP address to bind to as a webserver. "
                        "The default is 127.0.0.1 which is constrained to "
                        "the local machine.",
                        default="127.0.0.1")
    parser.add_argument("--reference-image",
                        help="An image of a reference volume to be used "
                        "for navigation.")
    parser.add_argument("--reference-segmentation",
                        help="A segmentation image of the reference volume "
                        "to be used for navigation.")
    parser.add_argument("--point-correspondence-file",
                        help="A .json file containing arrays of moving "
                        "and reference points to be used to warp the reference"
                        " frame into the moving frame.")
    args = parser.parse_args()

    patch_tornado()
    if os.path.exists(args.output):
        points = np.array(json.load(open(args.output)), np.float32)
    else:
        points = []

    if args.detected:
        detected_points = np.array(json.load(open(args.detected)), np.float32)
    else:
        detected_points = None

    neuroglancer.set_server_bind_address(args.bind_address, bind_port=args.port)

    if args.coordinates:
        x0, x1, y0, y1, z0, z1 = list(map(int, args.coordinates.split(",")))
        points, outside_points = filter_points(points)
        if detected_points is not None:
            detected_points, _ = filter_points(detected_points)
        img = load_image(args.image, x0, x1, y0, y1, z0, z1)
        filenames = sorted(glob.glob(args.image))
        z_extent = len(filenames)
        y_extent, x_extent = tifffile.imread(filenames[0]).shape
        width = x1 - x0
        height = y1 - y0
        depth = z1 - z0
    else:
        img = load_image(args.image).astype(np.float32)
        x0 = y0 = z0 = 0
        z1, y1, x1 = img.shape
        z_extent, y_extent, x_extent = img.shape
        depth, height, width = img.shape

    if args.alt_image is not None:
        alt_image = load_image(args.alt_image, x0, x1, y0, y1, z0, z1)

    viewer = neuroglancer.Viewer()
    with viewer.txn() as txn:
        txn.voxel_size = voxel_size
        layer(txn, "image", img, gray_shader, 1.0, x0, y0, z0)
        if args.alt_image is not None:
            layer(txn, "alt_image", alt_image, green_shader, 1.0,
                  x0, y0, z0)
        if os.path.exists(args.segmentation):
            seg = tifffile.imread(args.segmentation).astype(np.uint32)
            seglayer(txn, "segmentation", seg, x0, y0, z0)
        x, y, z = [np.array([_[idx] for _ in points]) for idx in range(3)]
        pointlayer(txn, "annotation", x, y, z, "yellow")
        if detected_points is not None:
            x, y, z = [np.array([_[idx] for _ in detected_points])
                       for idx in range(3)]
            pointlayer(txn, "detected", x, y, z, "green")
    save_fn = lambda s: save(args.output)
    annotate_fn = lambda s:action_handler(s, args.min_distance)
    delete_fn = lambda s:delete_handler(s, args.min_distance)
    viewer.actions.add("save", save_fn)
    viewer.actions.add("annotatepts", annotate_fn)
    viewer.actions.add("deletepts", delete_fn)
    with viewer.config_state.txn() as s:
        s.input_event_bindings.viewer["shift+keya"] = "annotatepts"
        s.input_event_bindings.viewer["shift+keys"] = "save"
        s.input_event_bindings.viewer["shift+keyd"] = "deletepts"
    print("Editing viewer: %s" % viewer.get_viewer_url())
    webbrowser.open_new(viewer.get_viewer_url())
    if args.reference_image is not None:
        ref_img = tifffile.imread(args.reference_image)
        ref_seg = tifffile.imread(args.reference_segmentation)
        with open(args.point_correspondence_file) as fd:
            d = json.load(fd)
        moving = np.array(d["moving"])
        reference = np.array(d["reference"])
        nav_viewer = NavViewer(ref_img, ref_seg, moving, reference,
                               (z_extent, y_extent, x_extent))
        nav_viewer.bind()
        sample = np.random.permutation(
            len(points) + len(outside_points))[:10000]
        pts = np.array(points+outside_points)[sample, ::-1]
        nav_viewer.add_points(pts)
        print("Navigating viewer: %s" % nav_viewer.viewer.get_viewer_url())
    print("Hit control-c to exit")
    while True:
        time.sleep(10)


if __name__=="__main__":
    main()
