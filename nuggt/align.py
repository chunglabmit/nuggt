"""align.py - an alignment tool


"""

import argparse
from copy import deepcopy
import logging
import json
import neuroglancer
import numpy as np
import os
from scipy.ndimage import map_coordinates
import tifffile
import time
import webbrowser

from .utils.warp import Warper

# Monkey-patch neuroglancer.PointAnnotationLayer to have a color

if not hasattr(neuroglancer.PointAnnotationLayer, "annotation_color"):
    from neuroglancer.viewer_state import  wrapped_property, optional, text_type
    neuroglancer.PointAnnotationLayer.annotation_color = \
        wrapped_property('annotationColor', optional(text_type))


def parse_args():
    parser = argparse.ArgumentParser(description="Neuroglancer Aligner")
    parser.add_argument("--reference-image",
                        help="Path to reference image file",
                        required=True)
    parser.add_argument("--moving-image",
                        help="Path to image file for image to be aligned",
                        required=True)
    parser.add_argument("--points",
                        help="Path to point-correspondence file",
                        required=True)
    parser.add_argument("--no-launch",
                        help="Don't launch browsers on startup",
                        default="false",
                        action="store_true")
    parser.add_argument("--ip-address",
                        help="IP address interface to use for http",
                        default=None)
    parser.add_argument("--port",
                        type=int,
                        default=None,
                        help="Port # for http. Default = let program choose")
    return parser.parse_args()


class ViewerPair:
    """The viewer pair maintains two neuroglancer viewers

    We maintain a reference viewer for the reference image and a moving
    viewer for the image to be aligned. The reference viewer has the following
    layers:
    * reference: the reference image
    * alignment: the image to be aligned, in the reference coordinate frame
    * correspondence-points: the annotation points in the reference frame
    * edit: an annotation layer containing the point being edited

    The moving image viewer has the following layers:
    * image: the moving image
    * correspondence-points: the annotation points in the moving image
                             coordinate frame
    * edit: an annotation layer containing the point being edited
    """

    REFERENCE = "reference"
    MOVING = "moving"
    ALIGNMENT = "alignment"
    CORRESPONDENCE_POINTS = "correspondence-points"
    IMAGE = "image"
    EDIT = "edit"
    EDIT_ACTION = "edit"
    ANNOTATE_ACTION = "annotate"
    DONE_KEY = "shift+keyd"
    DONE_ACTION = "done-with-point"
    EDIT_KEY = "shift+keye"
    SAVE_KEY = "shift+keys"
    SAVE_ACTION = "save-points"
    WARP_KEY = "shift+keyw"
    WARP_ACTION = "warp"

    EDIT_ANNOTATION_COLOR="#FF0000"

    REFERENCE_SHADER = """
void main() {
  emitRGB(vec3(0, toNormalized(getDataValue()), 0));
}
    """

    ALIGNMENT_SHADER = """
void main() {
  emitRGB(vec3(toNormalized(getDataValue()), 0, 
               toNormalized(getDataValue())));
}
        """

    IMAGE_SHADER="""
void main() {
  emitGrayscale(toNormalized(getDataValue()));
}
"""

    def __init__(self, reference_image, moving_image, points_file):
        """Constructor

        :param reference_image: align to this image
        :param moving_image: align this image
        :param points_file: where to load and store points
        """
        self.reference_image = reference_image
        self.moving_image = moving_image
        self.decimation = max(1, np.min(reference_image.shape) // 5)
        self.alignment_image = np.zeros(self.reference_image.shape,
                                        np.float32)
        self.reference_viewer = neuroglancer.Viewer()
        self.moving_viewer = neuroglancer.Viewer()
        self.points_file = points_file
        self.load_points()
        self.init_state()

    def load_points(self):
        """Load reference/moving points from the points file"""
        if not os.path.exists(self.points_file):
            self.reference_pts = []
            self.moving_pts = []
        else:
            with open(self.points_file, "r") as fd:
                d = json.load(fd)
            self.reference_pts = d[self.REFERENCE]
            self.moving_pts = d[self.MOVING]

    def save_points(self):
        """Save reference / moving points to the points file"""
        with open(self.points_file, "w") as fd:
            json.dump({
                self.REFERENCE: self.reference_pts,
                self.MOVING: self.moving_pts
            }, fd)

    def init_state(self):
        """Initialize each of the viewers' states"""
        self.init_reference_state()
        self.init_moving_state()

    @property
    def annotation_reference_pts(self):
        """Reference points in x, y, z order"""
        return [_[::-1] for _ in self.reference_pts]

    @property
    def annotation_moving_pts(self):
        """Moving points in x, y, z order"""
        return [_[::-1] for _ in self.moving_pts]

    def init_reference_state(self):
        """Initialize the state of the reference viewer"""
        with self.reference_viewer.txn() as s:
            s.layers[self.REFERENCE] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(self.reference_image),
                shader=self.REFERENCE_SHADER
            )
            s.layers[self.ALIGNMENT] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(self.alignment_image),
                shader = self.ALIGNMENT_SHADER
            )
            s.layers[self.CORRESPONDENCE_POINTS] = \
                neuroglancer.PointAnnotationLayer(
                    points=self.annotation_reference_pts)
            s.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                annotation_color=self.EDIT_ANNOTATION_COLOR
            )
        self.init_actions(self.reference_viewer,
                          self.on_reference_annotate)

    def init_actions(self, viewer, on_annotate):
        """Initialize the actions for a viewer

        :param viewer: the reference or moving viewer
        :param on_edit: the function to execute when the user wants to edit
        """
        viewer.actions.add(self.ANNOTATE_ACTION, on_annotate)
        viewer.actions.add(self.DONE_ACTION, self.on_done)
        viewer.actions.add(self.EDIT_ACTION, self.on_edit)
        viewer.actions.add(self.SAVE_ACTION, self.on_save)
        viewer.actions.add(self.WARP_ACTION, self.on_warp)
        with viewer.config_state.txn() as s:
            s.input_event_bindings.viewer[self.DONE_KEY] = self.DONE_ACTION
            s.input_event_bindings.viewer[self.EDIT_KEY] = self.EDIT_ACTION
            s.input_event_bindings.viewer[self.SAVE_KEY] = self.SAVE_ACTION
            s.input_event_bindings.viewer[self.WARP_KEY] = self.WARP_ACTION

    def init_moving_state(self):
        """Initialize the state of the moving viewer"""
        with self.moving_viewer.txn() as s:
            s.layers[self.IMAGE] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(self.moving_image),
                shader=self.IMAGE_SHADER
            )
            s.layers[self.CORRESPONDENCE_POINTS] = \
                neuroglancer.PointAnnotationLayer(
                    points=self.annotation_moving_pts)
            s.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                annotation_color=self.EDIT_ANNOTATION_COLOR
            )
        self.init_actions(self.moving_viewer, self.on_moving_annotate)

    def on_reference_annotate(self, s):
        """Handle an edit in the reference viewer

        :param s: the current state
        """
        point = s.mouse_voxel_coordinates
        with self.reference_viewer.config_state.txn() as cs:
            cs.status_messages[self.EDIT] = "Edit point: %d %d %d" % \
                tuple(point.tolist())

        with self.reference_viewer.txn() as txn:
            layer = neuroglancer.PointAnnotationLayer(
                points=[point.tolist()],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.layers[self.EDIT] = layer

    def on_moving_annotate(self, s):
        """Handle an edit in the moving viewer

        :param s: the current state
        """
        point = s.mouse_voxel_coordinates
        with self.reference_viewer.config_state.txn() as cs:
            cs.status_messages[self.EDIT] = "Edit point: %d %d %d" % \
                tuple(point.tolist())

        with self.moving_viewer.txn() as txn:
            layer = neuroglancer.PointAnnotationLayer(
                points=[point.tolist()],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.layers[self.EDIT] = layer

    def on_edit(self, s):
        """Transfer the currently selected point to the edit annotation"""
        layer = s.viewerState.layers[self.CORRESPONDENCE_POINTS].layer
        d = layer.to_json()
        if "selectedAnnotation" in d:
            idx = int(d["selectedAnnotation"])
            self.capture_points()
            reference = self.reference_pts[idx][::-1]
            moving = self.moving_pts[idx][::-1]
            del self.reference_pts[idx]
            del self.moving_pts[idx]
            with self.reference_viewer.txn() as txn:
                txn.layers[self.CORRESPONDENCE_POINTS] = \
                    neuroglancer.PointAnnotationLayer(
                        points=self.annotation_reference_pts)
                txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                    points=[reference],
                    annotation_color=self.EDIT_ANNOTATION_COLOR)
                txn.position.voxel_coordinates = reference
            with self.moving_viewer.txn() as txn:
                txn.layers[self.CORRESPONDENCE_POINTS] = \
                    neuroglancer.PointAnnotationLayer(
                        points=self.annotation_moving_pts)
                txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                    points=[moving],
                    annotation_color=self.EDIT_ANNOTATION_COLOR)
                txn.position.voxel_coordinates = moving

    def on_done(self, s):
        """Handle editing done"""
        try:
            ma = self.moving_viewer.state.layers[self.EDIT].annotations
        except AttributeError:
            ma = self.moving_viewer.state.layers[self.EDIT].points
        try:
            ra = self.reference_viewer.state.layers[self.EDIT].annotations
        except AttributeError:
            ra = self.reference_viewer.state.layers[self.EDIT].points
        if len(ma) == 1 and len(ra) == 1:
            mp = ma[0].point
            rp = ra[0].point
            self.append_point(self.moving_viewer, mp)
            self.append_point(self.reference_viewer, rp)

    def append_point(self, viewer, point):
        with viewer.txn() as txn:
            layer = txn.layers[self.CORRESPONDENCE_POINTS]
            points = [_.point.tolist() for _ in layer.annotations]
            points.append(point.tolist())
            txn.layers[self.CORRESPONDENCE_POINTS] = \
                neuroglancer.PointAnnotationLayer(points=points)
            txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                annotation_color="#FF0000")

    def on_save(self, s):
        """Handle a point-save action

        :param s: the current state of whatever viewer
        """
        self.capture_points()
        self.save_points()
        for viewer in (self.reference_viewer, self.moving_viewer):
            with viewer.config_state.txn() as txn:
                txn.status_messages[self.EDIT] = "Saved point state"

    def capture_points(self):
        with self.reference_viewer.txn() as txn:
            layer = txn.layers[self.CORRESPONDENCE_POINTS].layer
            try:
                points = layer.annotations
                self.reference_pts = [_.point[::-1].tolist() for _ in points]
            except AttributeError:
                points = layer.points
                self.reference_pts = [_[::-1].tolist() for _ in points]

        with self.moving_viewer.txn() as txn:
            layer = txn.layers[self.CORRESPONDENCE_POINTS].layer
            try:
                points = layer.annotations
                self.moving_pts = [_.point[::-1].tolist() for _ in points]
            except AttributeError:
                points = layer.points
                self.moving_pts = [_[::-1].tolist() for _ in points]

    def on_warp(self, s):
        cs, generation = \
            self.reference_viewer.config_state.state_and_generation
        cs = deepcopy(cs)

        cs.status_messages[self.WARP_ACTION] = \
            "Warping alignment image to reference... (patience please)"
        self.reference_viewer.config_state.set_state(
             cs, existing_generation=generation)
        ioloop = neuroglancer.server.global_server.ioloop
        cb = ioloop._callbacks.pop()
        try:
            ioloop._run_callback(cb)
        except:
            ioloop._callbacks.push(cb)
        try:
            self.capture_points()
            self.align_image()
            with self.reference_viewer.txn() as txn:
                txn.layers[self.ALIGNMENT] = neuroglancer.ImageLayer(
                    source=neuroglancer.LocalVolume(self.alignment_image),
                    shader=self.ALIGNMENT_SHADER
                )
            with self.reference_viewer.config_state.txn() as txn:
                txn.status_messages[self.WARP_ACTION] = \
                    "Warping complete, thank you for your patience."
        except:
            txn.status_messages[self.WARP_ACTION] = \
                "Oh my, something went wrong. See console log for details."
            raise

    def align_image(self):
        """Warp the moving image into the reference image's space"""
        warper = Warper(self.reference_pts, self.moving_pts)
        inputs = [np.arange(0, self.reference_image.shape[_]+ self.decimation - 1,
                            self.decimation) for _ in range(3)]
        warper = warper.approximate(*inputs)
        src_coords = np.column_stack([_.flatten() for _ in np.mgrid[
                        0:self.reference_image.shape[0],
                        0:self.reference_image.shape[1],
                        0:self.reference_image.shape[2]]])
        ii, jj, kk = [_.reshape(self.reference_image.shape) for _ in
                      warper(src_coords).transpose()]
        map_coordinates(self.moving_image, [ii, jj, kk],
                        output=self.alignment_image)

    def print_viewers(self):
        """Print the URLs of the viewers to the console"""
        print("Reference viewer: %s" % repr(self.reference_viewer))
        print("Moving viewer: %s" % repr(self.moving_viewer))

    def launch_viewers(self):
        """Launch webpages for each of the viewers"""
        webbrowser.open_new(self.reference_viewer.get_viewer_url())
        webbrowser.open_new(self.moving_viewer.get_viewer_url())


def normalize_image(img):
    """Normalize an image for display in neuroglancer

    :param img: the 3d image to be displayed
    """
    img_max = max(1, np.percentile(img.flatten(), 95))
    return np.clip(img.astype(np.float32) / img_max, 0, 1)

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.ip_address is not None and args.port is not None:
        neuroglancer.set_server_bind_address(
            bind_address=args.ip_address,
            bind_port=args.port)
    elif args.ip_address is not None:
        neuroglancer.set_server_bind_address(
            bind_address=args.ip_address)
    elif args.port is not None:
        neuroglancer.set_server_bind_address(bind_port=args.port)
    logging.info("Reading reference image")
    reference_image = normalize_image(tifffile.imread(args.reference_image))
    logging.info("Reading moving image")
    moving_image = normalize_image(tifffile.imread(args.moving_image))
    vp = ViewerPair(reference_image, moving_image, args.points)
    if not args.no_launch:
        vp.launch_viewers()
    vp.print_viewers()
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
