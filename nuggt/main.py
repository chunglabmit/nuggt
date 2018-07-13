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
from scipy.spatial import KDTree

from neuroglancer.server import BaseRequestHandler
from .utils.ngutils import *
from .ngreference import  NGReference

viewer = None

COLOR_POINTS = "yellow"
COLOR_DETECTED_POINTS = "green"
COLOR_DELETING_POINTS = "red"

class NuggtViewer:
    """The neuroglancer viewer controller

    This holds the state for displaying the current edit window.
    """
    def __init__(self, img_path, alt_img_path, seg_path, points_file,
                 detected_points_file = None,
                 x0=None, x1=None, y0=None, y1=None, z0=None, z1=None,
                 min_distance=10):
        self.viewer = neuroglancer.Viewer()
        self.points_file = points_file
        self.img_path = img_path
        self.alt_img_path=alt_img_path
        self.seg_path=seg_path
        self.min_distance = min_distance
        if os.path.exists(points_file):
            with open(points_file) as fd:
                self.points = np.array(json.load(fd))
        else:
            self.points = np.zeros((0, 3), np.float32)
        if detected_points_file is not None:
            with open(detected_points_file) as fd:
                self.detected_points = json.load(fd)
        else:
            self.detected_points = None
        self.deleting_points = None
        self.box_coords = None
        filenames = sorted(glob.glob(img_path))
        if len(filenames) == 1:
            self.z_extent, self.y_extent, self.x_extent = \
                tifffile.imread(filenames[0]).shape
        else:
            self.y_extent, self.x_extent = tifffile.imread(filenames[0]).shape
            self.z_extent = len(filenames)
        if x0 is not None and x1 is not None:
            self.width = x1 - x0
            self.x0 = x0
            self.x1 = x1
        else:
            self.width = self.x_extent
            self.x0 = 0
            self.x1 = self.x_extent
        if y0 is not None and y1 is not None:
            self.height = y1 - y0
            self.y0 = y0
            self.y1 = y1
        else:
            self.height = self.y_extent
            self.y0 = 0
            self.y1 = self.height
        if z0 is not None and z1 is not None:
            self.depth = z1 - z0
            self.z0 = z0
            self.z1 = z1
        else:
            self.depth = self.z_extent
            self.z0 = 0
            self.z1 = self.z_extent
        self.display()
        save_fn = lambda s: self.save()
        annotate_fn = self.action_handler
        delete_fn = self.delete_handler
        self.viewer.actions.add("save", save_fn)
        self.viewer.actions.add("annotatepts", annotate_fn)
        self.viewer.actions.add("deletepts", delete_fn)
        self.viewer.actions.add("start-selection",
                                self.start_selection_handler)
        self.viewer.actions.add("extend-selection",
                                self.extend_selection_handler)
        self.viewer.actions.add("delete-selected",
                                self.delete_selected_handler)
        #
        # Hint: this page lets you type a character and see its code
        # https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code
        #
        with self.viewer.config_state.txn() as s:
            s.input_event_bindings.viewer["shift+keya"] = "annotatepts"
            s.input_event_bindings.viewer["shift+keys"] = "save"
            s.input_event_bindings.viewer["shift+keyd"] = "deletepts"
            s.input_event_bindings.viewer["bracketleft"] = "start-selection"
            s.input_event_bindings.viewer["bracketright"] = "extend-selection"
            s.input_event_bindings.viewer["shift+keyx"] = "delete-selected"

    @property
    def shape(self):
        """The size of the potential display volume"""
        return (self.z_extent, self.y_extent, self.x_extent)

    def center(self):
        with self.viewer.txn() as txn:
            txn.position.voxel_coordinates = \
                ((self.x0 + self.x1) / 2,
                 (self.y0 + self.y1) / 2,
                 (self.z0 + self.z1) / 2)

    def display(self):
        img = load_image(self.img_path, self.x0, self.x1, self.y0, self.y1,
                         self.z0, self.z1)
        if self.alt_img_path is not None:
            alt_img = load_image(self.alt_img_path, self.x0, self.x1,
                                 self.y0, self.y1, self.z0, self.z1)
        if self.seg_path is not None:
            seg = load_image(self.seg_path, self.x0, self.x1,
                             self.y0, self.y1, self.z0, self.z1)
        with self.viewer.txn() as txn:
            layer(txn, "image", img, gray_shader, 1.0,
                  self.x0, self.y0, self.z0)
            if self.alt_img_path is not None:
                layer(txn, "alt-image", alt_img, green_shader, 1.0,
                      self.x0, self.y0, self.z0)
            if self.seg_path is not None:
                seglayer(txn, "segmentation", seg, self.x0, self.y0, self.z0)
            self.display_points(txn, self.points, "annotation", COLOR_POINTS)
            if self.detected_points is not None:
                self.display_points(txn, self.detected_points, "detected",
                                    COLOR_DETECTED_POINTS)
            elif has_layer(txn, "detected"):
                del txn.layers["detected"]
            if self.deleting_points is not None:
                self.display_points(txn, self.deleting_points, "deleting",
                                    COLOR_DELETING_POINTS)
            elif has_layer(txn, "deleting"):
                del txn.layers["deleting"]

            if self.box_coords is not None:
                self.display_bounding_box(txn)
            elif has_layer(txn, "selection"):
                del txn.layers["selection"]
        self.center()

    def display_bounding_box(self, txn):
        box = neuroglancer.AxisAlignedBoundingBoxAnnotation()
        box.point_a = self.box_coords[0]
        box.point_b = self.box_coords[1]
        box.id = "selection"
        txn.layers["selection"] = neuroglancer.AnnotationLayer(
            annotations=[box])

    def display_points(self, txn, points, layer_name, color):
        mask = (points[:, 0] >= self.x0) & (points[:, 0] < self.x1) & \
               (points[:, 1] >= self.y0) & (points[:, 1] < self.y1) & \
               (points[:, 2] >= self.z0) & (points[:, 2] < self.z1)
        display_points = points[mask]
        pointlayer(txn, layer_name,
                   display_points[:, 0], display_points[:, 1],
                   display_points[:, 2],
                   color)

    def say(self, msg, category):
        with self.viewer.config_state.txn() as txn:
            txn.status_messages[category] = msg

    def action_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        neighbors = self.find_nearby_points(point)
        if len(neighbors) > 0:
            self.say("Point too close to some other point!", "annotation")
            return
        self.points = np.vstack((self.points, point))
        with self.viewer.txn() as txn:
            self.display_points(txn, self.points, "annotation", COLOR_POINTS)
        self.say("Added point at %.2f, %.2f, %.2f" %
                 (point[0], point[1], point[2]),
            "annotation")

    def find_nearby_points(self, point, return_index=False):
        diff = self.points - point[np.newaxis, :]
        distances = np.sqrt(np.sum(np.square(diff), 1))
        indexes = np.where(distances < self.min_distance)[0]
        if len(indexes) == 0:
            if return_index:
                return np.zeros((0, 3), np.float32), np.zeros(0, int)
            else:
                return np.zeros((0, 3), np.float32)
        result = self.points[indexes]
        order = np.argsort(distances[indexes])
        if return_index:
            return result[order], indexes[order]
        else:
            return result[order]

    def delete_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        neighbors, indexes = self.find_nearby_points(point, return_index=True)
        if len(neighbors) == 0:
            self.say("No nearby point", "delete")
            return
        to_delete = self.points[indexes[0]]
        self.points = np.delete(self.points, indexes[0], 0)
        with self.viewer.txn() as txn:
            self.display_points(txn, self.points, "annotation", COLOR_POINTS)
        self.say("Deleting %.2f, %.2f, %.2f" %
            (to_delete[0], to_delete[1], to_delete[2]), "delete")

    def partition_points(self):
        """Partition points inside/outside bounding box"""
        for idx in range(3):
            if self.box_coords[0][idx] == self.box_coords[1][idx]:
                self.box_coords[1][idx] += 1
        (x0, x1), (y0, y1), (z0, z1) = [
            [fn(self.box_coords[0][idx], self.box_coords[1][idx])
             for fn in (min, max)] for idx in range(3)]
        all_points = self.all_points
        mask = (all_points[:, 0] >= x0) & (all_points[:, 0] < x1) & \
               (all_points[:, 1] >= y0) & (all_points[:, 1] < y1) & \
               (all_points[:, 2] >= z0) & (all_points[:, 2] < z1)
        self.points, self.deleting_points = all_points[~mask], all_points[mask]
        with self.viewer.txn() as txn:
            self.display_points(txn, self.points, "annotation", COLOR_POINTS)
            self.display_points(txn, self.deleting_points,
                                "deleting", COLOR_DELETING_POINTS)
            self.display_bounding_box(txn)

    def start_selection_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        if self.box_coords is None:
            self.box_coords = [point, point + 20]
        else:
            self.box_coords[0] = point
        self.partition_points()

    def extend_selection_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        if self.box_coords is None:
            self.box_coords = [point-20, point]
        else:
            self.box_coords[1] = point
        self.partition_points()

    def delete_selected_handler(self, s):
        if self.box_coords is not None:
            self.box_coords = None
            self.deleting_points = None
            with self.viewer.txn() as txn:
                del txn.layers["selection"]
                del txn.layers["deleting"]

    @property
    def all_points(self):
        """Both the regular points and those in the delete bucket"""
        if self.deleting_points is not None:
            return np.vstack((self.points, self.deleting_points))
        else:
            return self.points

    def save(self):
        post_message_immediately(
            self.viewer, "save", "Saving annotations... patience")
        if os.path.exists(self.points_file):
            mtime = os.stat(self.points_file).st_mtime
            ext = time.strftime('.%Y-%m-%d_%H-%M-%S', time.localtime(mtime))
            os.rename(self.points_file, self.points_file + ext)
        with open(self.points_file, "w") as fd:
            fd.write("[\n")
            need_comma = False

            for x, y, z in self.all_points:
                if need_comma:
                    fd.write(",\n")
                else:
                    need_comma = True
                fd.write("  [%.2f,%.2f,%.2f]" % (x, y, z))
            fd.write("\n]\n")
        self.say("Saved annotations to %s" % self.points_file, "save")

    def reposition(self, x0, x1, y0, y1, z0, z1):
        """Reposition the UI between the given coordinates

        """
        self.points = self.all_points
        self.box_coords = None
        self.deleting_points = None
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.z0 = z0
        self.z1 = z1
        self.display()

def load_one_plane(imgpath, tfpath, x0, x1, y0, y1, z):
    plane = tifffile.imread(imgpath)[y0:y1, x0:x1]
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


class NavViewer(NGReference):

    def __init__(self, *args, **kwargs):
        super(NavViewer, self).__init__(*args, **kwargs)
        self.repositioning_log_file = None

    def bind(self):
        """Bind the nav viewer"""
        self.viewer.actions.add("jump", self.on_action)
        with self.viewer.config_state.txn() as s:
            s.input_event_bindings.viewer["keyj"] = "jump"

    def action_handler(self, s, moving_point):
        post_message_immediately(self.viewer,
                                 "jumping",
                                 "Repositioning viewer...patience")
        x0a = int(max(0, moving_point[2] - viewer.width // 2))
        x1a = int(min(viewer.x_extent, x0a + viewer.width))
        y0a = int(max(0, moving_point[1] - viewer.height //2))
        y1a = int(min(viewer.y_extent, y0a + viewer.height))
        z0a = int(max(0, moving_point[0] - viewer.depth // 2))
        z1a = int(min(viewer.z_extent, z0a + viewer.depth))
        viewer.reposition(x0a, x1a, y0a, y1a, z0a, z1a)
        with self.viewer.config_state.txn() as txn:
            txn.status_messages["jumping"] = "Viewer repositioned"
        if self.repositioning_log_file is not None:
            with open(self.repositioning_log_file, "a") as fd:
                json.dump(
                    dict(x0=x0a, x1=x1a, y0=y0a, y1=y1a, z0=z0a, z1=z1a), fd)
                fd.write("\n")
        else:
            print(json.dumps(dict(x0=x0a, x1=x1a, y0=y0a, y1=y1a, z0=z0a, z1=z1a)))


def main():
    global viewer

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
                        help="Path to existing segmentation file (optional)")
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
    parser.add_argument("--static-content-source",
                        default=None,
                        help="The URL of the static content source, e.g. "
                        "http://localhost:8080 if being served via npm.")
    parser.add_argument("--reference-image",
                        help="An image of a reference volume to be used "
                        "for navigation.")
    parser.add_argument("--reference-segmentation",
                        help="A segmentation image of the reference volume "
                        "to be used for navigation.")
    parser.add_argument("--reference-points",
                        help="The point annotations, transformed into the "
                             "reference space.")
    parser.add_argument("--point-correspondence-file",
                        help="A .json file containing arrays of moving "
                        "and reference points to be used to warp the reference"
                        " frame into the moving frame.")
    parser.add_argument("--repositioning-log-file",
                        default=None,
                        help="This file saves a record of the coordinates "
                        "of each repositioning in order to keep track of "
                        "which areas have been visited.")
    args = parser.parse_args()
    neuroglancer.set_server_bind_address(args.bind_address, bind_port=args.port)
    if args.static_content_source is not None:
        neuroglancer.set_static_content_source(url=args.static_content_source)

    if args.coordinates:
        x0, x1, y0, y1, z0, z1 = list(map(int, args.coordinates.split(",")))
        viewer = NuggtViewer(args.image,
                             args.alt_image,
                             args.segmentation,
                             args.output,
                             args.detected,
                             x0, x1, y0, y1, z0, z1,
                             min_distance=args.min_distance)
    else:
        viewer = NuggtViewer(args.image,
                             args.alt_image,
                             args.segmentation,
                             args.output,
                             args.detected,
                             min_distance=args.min_distance)

    print("Editing viewer: %s" % viewer.viewer.get_viewer_url())
    webbrowser.open_new(viewer.viewer.get_viewer_url())
    if args.reference_image is not None:
        ref_img = tifffile.imread(args.reference_image).astype(np.float32)
        ref_seg = tifffile.imread(args.reference_segmentation).astype(np.uint16)
        with open(args.point_correspondence_file) as fd:
            d = json.load(fd)
        moving = np.array(d["moving"])
        reference = np.array(d["reference"])
        nav_viewer = NavViewer(ref_img, ref_seg, moving, reference,
                               viewer.shape)
        nav_viewer.bind()
        if args.repositioning_log_file is not None:
            nav_viewer.repositioning_log_file = args.repositioning_log_file
        sample = np.random.permutation(len(viewer.points))[:10000]
        if args.reference_points is not None:
            with open(args.reference_points) as fd:
                rp = np.array(json.load(fd))
                pts = rp[sample, ::-1]
        else:
            pts = viewer.points[sample, ::-1]
        nav_viewer.add_points(pts)
        print("Navigating viewer: %s" % nav_viewer.viewer.get_viewer_url())
    print("Hit control-c to exit")
    while True:
        time.sleep(10)


if __name__=="__main__":
    main()
