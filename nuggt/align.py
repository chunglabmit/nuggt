"""align.py - an alignment tool


"""

import argparse
from copy import deepcopy
import logging
import json
import multiprocessing
import neuroglancer
import numpy as np
import os
from scipy.ndimage import map_coordinates
import tifffile
import time
import webbrowser

from .utils.warp import Warper
from .utils.ngutils import layer, seglayer, pointlayer
from .utils.ngutils import red_shader, gray_shader, green_shader
from .utils.ngutils import soft_max_brightness

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
    parser.add_argument("--segmentation",
                        help="Path to the segmentation file accompanying "
                        "the reference image.",
                        default=None)
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
    parser.add_argument("--static-content-source",
                        default=None,
                        help="Obsolete - this no longer has any effect.")
    parser.add_argument("--reference-voxel-size",
                        help="X, Y and Z size of voxels, separated by "
                        "commas, e.g. \"1.6,1.6,1.0\"",
                        default="1.0,1.0,1.0")
    parser.add_argument("--moving-voxel-size",
                        help="X, Y and Z size of voxels, separated by "
                        "commas, e.g. \"1.6,1.6,1.0\"",
                        default="1.0,1.0,1.0")
    parser.add_argument("--min-distance",
                        type=float,
                        default=1.0,
                        help="Minimum distance between any two annotations.")
    parser.add_argument("--n-workers",
                        type=int,
                        default=multiprocessing.cpu_count(),
                        help="# of workers to use during warping")
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
    SEGMENTATION = "segmentation"

    ANNOTATE_ACTION = "annotate"
    BRIGHTER_ACTION = "brighter"
    DIMMER_ACTION = "dimmer"
    CLEAR_ACTION = "clear"
    DONE_ACTION = "done-with-point"
    EDIT_ACTION = "edit"
    NEXT_ACTION = "next"
    PREVIOUS_ACTION = "previous"
    REFERENCE_BRIGHTER_ACTION = "reference-brighter"
    REFERENCE_DIMMER_ACTION = "reference-dimmer"
    REFRESH_ACTION = "refresh-view"
    REDO_ACTION = "redo"
    SAVE_ACTION = "save-points"
    TRANSLATE_ACTION = "translate-point"
    UNDO_ACTION = "undo"
    WARP_ACTION = "warp"

    BRIGHTER_KEY = "shift+equal"
    CLEAR_KEY = "shift+keyc"
    DIMMER_KEY = "minus"
    DONE_KEY = "shift+keyd"
    EDIT_KEY = "shift+keye"
    NEXT_KEY = "shift+keyn"
    PREVIOUS_KEY = "shift+keyp"
    REFERENCE_BRIGHTER_KEY = "shift+alt+equal"
    REFERENCE_DIMMER_KEY = "alt+minus"
    REFRESH_KEY = "shift+keyr"
    SAVE_KEY = "shift+keys"
    REDO_KEY = "control+keyy"
    TRANSLATE_KEY = "shift+keyt"
    UNDO_KEY = "control+keyz"
    WARP_KEY = "shift+keyw"

    EDIT_ANNOTATION_COLOR="#FF0000"

    REFERENCE_SHADER = """
void main() {
  emitRGB(vec3(0, toNormalized(getDataValue()), 0));
}
    """

    ALIGNMENT_SHADER = """
void main() {
  emitGrayscale(toNormalized(getDataValue()));
}
        """

    IMAGE_SHADER="""
void main() {
  emitGrayscale(toNormalized(getDataValue()));
}
"""
    #
    # For multiprocessing - dictionaries keyed on id(self)
    #
    moving_images = {}
    alignment_raw = {}
    warpers = {}
    alignment_buffers = {}

    def __init__(self, reference_image, moving_image, segmentation,
                 points_file, reference_voxel_size, moving_voxel_size,
                 min_distance=1.0,
                 n_workers=multiprocessing.cpu_count()):
        """Constructor

        :param reference_image: align to this image
        :param moving_image: align this image
        :param segmentation: the segmentation associated with the reference
        image or None if no segmentation.
        :param points_file: where to load and store points
        :param reference_voxel_size: a 3-tuple giving the X, Y and Z voxel
        size in nanometers.
        :param moving_voxel_size: the voxel size for the moving image
        :param min_distance: the minimum allowed distance between any two points
        :param n_workers: # of workers to use when warping
        """
        self.reference_image = reference_image
        self.moving_image = moving_image
        self.segmentation = segmentation
        self.n_workers = n_workers
        self.moving_images[id(self)] = moving_image
        self.decimation = max(1, np.min(reference_image.shape) // 5)
        n_elems = int(np.prod(self.reference_image.shape))
        alignment_raw = multiprocessing.RawArray(
            'f', n_elems)
        self.alignment_raw[id(self)] = alignment_raw
        self.reference_viewer = neuroglancer.Viewer()
        self.moving_viewer = neuroglancer.Viewer()
        self.points_file = points_file
        self.warper = None
        self.reference_voxel_size = reference_voxel_size
        self.moving_voxel_size = moving_voxel_size
        self.reference_brightness = 1.0
        self.moving_brightness = 1.0
        self.min_distance = min_distance
        self.load_points()
        self.init_state()
        self.refresh_brightness()

    @property
    def alignment_image(self):
        alignment_raw = self.alignment_raw[id(self)]
        n_elems = np.prod(self.reference_image.shape)
        return np.frombuffer(
            alignment_raw, np.float32, count=n_elems)\
            .reshape(self.reference_image.shape)

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
        self.init_actions(self.reference_viewer,
                          self.on_reference_annotate)
        self.init_actions(self.moving_viewer, self.on_moving_annotate)
        self.undo_stack = []
        self.redo_stack = []
        self.selection_index = len(self.reference_pts)
        self.refresh()
        self.update_after_edit()

    @property
    def annotation_reference_pts(self):
        """Reference points in z, y, x order"""
        #return [_[::-1] for _ in self.reference_pts]
        return self.reference_pts

    @property
    def annotation_moving_pts(self):
        """Moving points in z, y, x order"""
        #return [_[::-1] for _ in self.moving_pts]
        return self.moving_pts

    def init_actions(self, viewer, on_annotate):
        """Initialize the actions for a viewer

        :param viewer: the reference or moving viewer
        :param on_edit: the function to execute when the user wants to edit
        """
        viewer.actions.add(self.ANNOTATE_ACTION, on_annotate)
        viewer.actions.add(self.BRIGHTER_ACTION, self.on_brighter)
        viewer.actions.add(self.CLEAR_ACTION, self.on_clear)
        viewer.actions.add(self.DIMMER_ACTION, self.on_dimmer)
        viewer.actions.add(self.DONE_ACTION, self.on_done)
        viewer.actions.add(self.EDIT_ACTION, self.on_edit)
        viewer.actions.add(self.NEXT_ACTION, self.on_next)
        viewer.actions.add(self.PREVIOUS_ACTION, self.on_previous)
        viewer.actions.add(self.REFERENCE_BRIGHTER_ACTION,
                           self.on_reference_brighter)
        viewer.actions.add(self.REFERENCE_DIMMER_ACTION,
                           self.on_reference_dimmer)
        viewer.actions.add(self.REFRESH_ACTION, self.on_refresh)
        viewer.actions.add(self.SAVE_ACTION, self.on_save)
        viewer.actions.add(self.REDO_ACTION, self.on_redo)
        viewer.actions.add(self.UNDO_ACTION, self.on_undo)
        viewer.actions.add(self.WARP_ACTION, self.on_warp)
        #
        # Translate can only be done from reference to moving
        #
        if viewer == self.reference_viewer:
            viewer.actions.add(self.TRANSLATE_ACTION, self.on_translate)
        with viewer.config_state.txn() as s:
            bindings_viewer = s.input_event_bindings.viewer
            bindings_viewer[self.BRIGHTER_KEY] = self.BRIGHTER_ACTION
            bindings_viewer[self.CLEAR_KEY] = self.CLEAR_ACTION
            bindings_viewer[self.DIMMER_KEY] = self.DIMMER_ACTION
            bindings_viewer[self.DONE_KEY] = self.DONE_ACTION
            bindings_viewer[self.EDIT_KEY] = self.EDIT_ACTION
            bindings_viewer[self.NEXT_KEY] = self.NEXT_ACTION
            bindings_viewer[self.PREVIOUS_KEY] = self.PREVIOUS_ACTION
            bindings_viewer[self.REFERENCE_BRIGHTER_KEY] = \
                self.REFERENCE_BRIGHTER_ACTION
            bindings_viewer[self.REFERENCE_DIMMER_KEY] = \
                self.REFERENCE_DIMMER_ACTION
            bindings_viewer[self.REFRESH_KEY] = self.REFRESH_ACTION
            bindings_viewer[self.SAVE_KEY] = self.SAVE_ACTION
            bindings_viewer[self.REDO_KEY] = self.REDO_ACTION
            bindings_viewer[self.UNDO_KEY] = self.UNDO_ACTION
            bindings_viewer[self.WARP_KEY] = self.WARP_ACTION
            if viewer == self.reference_viewer:
                bindings_viewer[self.TRANSLATE_KEY] = self.TRANSLATE_ACTION

    def on_reference_annotate(self, s):
        """Handle an edit in the reference viewer

        :param s: the current state
        """
        point = s.mouse_voxel_coordinates
        reference_points = np.array(self.reference_pts)
        if len(reference_points) > 0:
            distances = np.sqrt(np.sum(np.square(
                reference_points - point[np.newaxis, ::-1]), 1))
            if np.min(distances) < self.min_distance:
                self.post_message(
                    self.reference_viewer, self.EDIT,
                    "Point at %d %d %d is too close to some other point" %
                    tuple(point.tolist()))
                return
        msg = "Edit point: %d %d %d" %  tuple(point.tolist())
        self.post_message(self.reference_viewer, self.EDIT, msg)

        with self.reference_viewer.txn() as txn:
            layer = neuroglancer.PointAnnotationLayer(
                points=[point.tolist()],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.layers[self.EDIT] = layer

    def post_message(self, viewer, kind, msg):
        """Post a message to a viewer

        :param viewer: the reference or moving viewer
        :param kind: the kind of message - a name slot for the message
        :param msg: the message to post
        """
        if viewer is None:
            self.post_message(self.reference_viewer, kind, msg)
            self.post_message(self.moving_viewer, kind, msg)
        else:
            with viewer.config_state.txn() as cs:
                cs.status_messages[kind] = msg

    def on_moving_annotate(self, s):
        """Handle an edit in the moving viewer

        :param s: the current state
        """
        point = s.mouse_voxel_coordinates
        moving_points = np.array(self.moving_pts)
        if len(moving_points) > 0:
            distances = np.sqrt(np.sum(np.square(
                moving_points - point[np.newaxis, ::-1]), 1))
            if np.min(distances) < self.min_distance:
                self.post_message(
                    self.moving_viewer, self.EDIT,
                    "Point at %d %d %d is too close to some other point" %
                    tuple(point.tolist()))
                return
        msg = "Edit point: %d %d %d" %  tuple(point.tolist())
        self.post_message(self.moving_viewer, self.EDIT, msg)

        with self.moving_viewer.txn() as txn:
            layer = neuroglancer.PointAnnotationLayer(
                points=[point.tolist()],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.layers[self.EDIT] = layer

    def on_brighter(self, s):
        self.brighter()

    def brighter(self):
        self.moving_brightness *= 1.25
        self.refresh_brightness()

    def on_reference_brighter(self, s):
        self.reference_brighter()

    def reference_brighter(self):
        self.reference_brightness *= 1.25
        self.refresh_brightness()

    def on_reference_dimmer(self, s):
        self.reference_dimmer()

    def reference_dimmer(self):
        self.reference_brightness = self.reference_brightness / 1.25
        self.refresh_brightness()

    def on_clear(self, s):
        """Clear the current edit annotation"""
        self.clear()

    def clear(self):
        """Clear the edit annotation from the UI"""
        with self.reference_viewer.txn() as txn:
            txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                annotation_color=self.EDIT_ANNOTATION_COLOR)
        with self.moving_viewer.txn() as txn:
            txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                annotation_color=self.EDIT_ANNOTATION_COLOR)

    def on_dimmer(self, s):
        self.dimmer()

    def dimmer(self):
        self.moving_brightness = self.moving_brightness / 1.25
        self.refresh_brightness()

    def refresh_brightness(self):
        max_reference_img = soft_max_brightness(self.reference_image)
        max_moving_img = soft_max_brightness(self.moving_image)
        with self.reference_viewer.txn() as txn:
            txn.layers[self.REFERENCE].layer.shader = \
                red_shader % (self.reference_brightness / max_reference_img)
            txn.layers[self.ALIGNMENT].layer.shader = \
                green_shader % (self.moving_brightness / max_moving_img)
        with self.moving_viewer.txn() as txn:
            txn.layers[self.IMAGE].layer.shader = \
                gray_shader % (self.moving_brightness / max_moving_img)

    def on_edit(self, s):
        """Transfer the currently selected point to the edit annotation"""
        layer = s.viewerState.layers[self.CORRESPONDENCE_POINTS].layer
        d = layer.to_json()
        if "selectedAnnotation" in d:
            idx = int(d["selectedAnnotation"])
            self.selection_index = idx
            self.edit_point(self.selection_index)
            self.redo_stack.clear()

    def edit_point(self, idx, add_to_undo=True):
        reference, moving = self.remove_point(idx, add_to_undo)
        with self.reference_viewer.txn() as txn:
            #txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
            #    points=[reference[::-1]],
            #    annotation_color=self.EDIT_ANNOTATION_COLOR)
            pointlayer(
                txn, self.EDIT, 
                [reference[0]], [reference[1]], [reference[2]],
                color=self.EDIT_ANNOTATION_COLOR,
                voxel_size=self.reference_voxel_size)
            #txn.position.voxel_coordinates = reference[::-1]
            txn.position = reference[::-1]
        with self.moving_viewer.txn() as txn:
            #txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
            #    points=[moving[::-1]],
            #    annotation_color=self.EDIT_ANNOTATION_COLOR)
            pointlayer(
                txn, self.EDIT, 
                [moving[0]], [moving[1]], [moving[2]],
                color=self.EDIT_ANNOTATION_COLOR,
                voxel_size=self.moving_voxel_size)
            #txn.position.voxel_coordinates = moving[::-1]
            txn.position = moving[::-1]

    def on_next(self, s):
        """Save the current edit and move to the next point"""
        self.on_done(s)
        if len(self.reference_pts) > 0:
            self.selection_index = \
                (self.selection_index + 1) % len(self.reference_pts)
            self.edit_point(self.selection_index)
            self.redo_stack.clear()

    def on_previous(self, s):
        """Save the current edit and move to the previous point"""
        self.on_done(s)
        if len(self.reference_pts) > 0:
            self.selection_index = \
                len(self.reference_pts) - 1 if self.selection_index == 0 \
                else self.selection_index - 1
            self.edit_point(self.selection_index)
            self.redo_stack.clear()

    def on_done(self, s):
        """Handle editing done"""
        rp = self.get_reference_edit_point()
        mp = self.get_moving_edit_point()
        if mp and rp:
            self.add_point(self.selection_index, rp, mp)
            self.clear()
            self.redo_stack.clear()

    def get_moving_edit_point(self):
        try:
            ma = self.moving_viewer.state.layers[self.EDIT].annotations
        except AttributeError:
            ma = self.moving_viewer.state.layers[self.EDIT].points
        if len(ma) == 0:
            return None
        points = ma[0].point.tolist()[::-1] # reverse it back to zyx order
        self.post_message(self.moving_viewer, self.EDIT,
                "Get the moving edit point at %d, %d, %d" %
                tuple(points)[::-1])
        return points

    def get_reference_edit_point(self):
        """Get the current edit point in the reference frame"""
        try:
            ra = self.reference_viewer.state.layers[self.EDIT].annotations
        except AttributeError:
            ra = self.reference_viewer.state.layers[self.EDIT].points
        if len(ra) == 0:
            return None
        points = ra[0].point.tolist()[::-1] # reverse it back to zyx order
        self.post_message(self.reference_viewer, self.EDIT,
                "Get the reference edit point at %d, %d, %d" %
                tuple(points)[::-1])
        return points

    def add_point(self, idx, reference_point, moving_point, add_to_undo=True):
        """Add a point to the reference and moving points list

        :param idx: where to add the point
        :param reference_point: the point to add in the reference space,
               in Z, Y, X order
        :param moving_point: the point to add in the moving space,
               in Z, Y, X order
        :param add_to_undo: True to add a "delete" operation to the undo stack,
        False to add it to the redo stack.
        """
        #
        # Tasks to complete:
        #     Add the points to the points lists at the current insert loc
        #     Enter an appropriate undo entry
        #     Post an appropriate message.
        #     Update the UI
        #
        self.reference_pts.insert(idx, reference_point)
        self.post_message(self.reference_viewer, self.EDIT,
                          "Added point at %d, %d, %d" %
                          tuple(reference_point[::-1]))
        self.moving_pts.insert(idx, moving_point)
        self.post_message(self.moving_viewer, self.EDIT,
                          "Added point at %d, %d, %d" %
                          tuple(moving_point[::-1]))
        entry = (self.edit_point, (idx, not add_to_undo))
        if add_to_undo:
            self.undo_stack.append(entry)
        else:
            self.redo_stack.append(entry)
        self.update_after_edit()

    def remove_point(self, idx, add_to_undo=True):
        """Remove the point at the given index

        :param idx: the index into the reference_pts and moving_pts array
        :param add_to_undo: True to add the undo operation to the undo stack,
        false to add it to the redo stack.
        :returns: the reference and moving points removed.
        """
        reference_point = self.reference_pts.pop(idx)
        self.post_message(self.reference_viewer, self.EDIT,
                          "removed point %d at %d, %d, %d" %
                          tuple([idx] + list(reference_point[::-1])))
        moving_point = self.moving_pts.pop(idx)
        self.post_message(self.moving_viewer, self.EDIT,
                          "removed point %d at %d, %d, %d" %
                          tuple([idx] + list(moving_point[::-1])))
        entry = (self.add_point, (idx, reference_point, moving_point,
                                  not add_to_undo))
        if add_to_undo:
            self.undo_stack.append(entry)
        else:
            self.redo_stack.append(entry)
        self.update_after_edit()
        return reference_point, moving_point

    def update_after_edit(self):
        for viewer, points, voxel_size in ((self.reference_viewer,
                                            self.annotation_reference_pts,
                                            self.reference_voxel_size),
                                           (self.moving_viewer,
                                            self.annotation_moving_pts,
                                            self.moving_voxel_size)):
            points = np.array(points, dtype=np.float32)
            if len(points) == 0:
                points = points.reshape(0, 3)
            with viewer.txn() as txn:
                pointlayer(
                    txn, self.CORRESPONDENCE_POINTS,
                    points[:, 0], points[:, 1], points[:, 2],
                    voxel_size=voxel_size)
                pointlayer(
                    txn, self.EDIT, np.zeros(0), np.zeros(0), np.zeros(0),
                    color=self.EDIT_ANNOTATION_COLOR, voxel_size=voxel_size)

    def on_refresh(self, s):
        self.refresh()

    def refresh(self):
        """Refresh both views"""
        with self.moving_viewer.txn() as s:
            s.dimensions = neuroglancer.CoordinateSpace(
                  names=["x", "y", "z"],
                  units=["µm"],
                  scales=self.moving_voxel_size)
            layer(s, self.IMAGE, self.moving_image, gray_shader,
                  self.moving_brightness,
                  voxel_size=self.moving_voxel_size)
        with self.reference_viewer.txn() as s:
            s.dimensions = neuroglancer.CoordinateSpace(
                  names=["x", "y", "z"],
                  units=["µm"],
                  scales=self.reference_voxel_size)
            layer(s, self.REFERENCE, self.reference_image, red_shader,
                  self.reference_brightness,
                  voxel_size=self.reference_voxel_size)
            layer(s, self.ALIGNMENT, self.alignment_image, green_shader,
                  self.moving_brightness,
                  voxel_size=self.moving_voxel_size)
            if self.segmentation is not None:
                seglayer(s, self.SEGMENTATION, self.segmentation)

    def on_undo(self, s):
        """Undo the last operation"""
        if len(self.undo_stack) > 0:
            undo = self.undo_stack.pop(-1)
            undo[0](*undo[1])
        else:
            self.post_message(None, self.EDIT, "Nothing to undo")

    def on_redo(self, s):
        """Redo the last undo operation"""
        if len(self.redo_stack) > 0:
            redo = self.redo_stack.pop(-1)
            redo[0](*redo[1])
        else:
            self.post_message(None, self.EDIT, "Nothing to redo")

    def on_translate(self, s):
        """Translate the editing coordinate in the reference frame to moving"""
        rp = self.get_reference_edit_point()
        if self.warper != None and rp:
            mp = self.warper(np.atleast_2d(rp))[0]
            with self.moving_viewer.txn() as txn:
                txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                    points=[mp[::-1]],
                    annotation_color=self.EDIT_ANNOTATION_COLOR)
                txn.position = mp[::-1]

    def on_save(self, s):
        """Handle a point-save action

        :param s: the current state of whatever viewer
        """
        self.save_points()
        for viewer in (self.reference_viewer, self.moving_viewer):
            self.post_message(viewer, self.EDIT, "Saved point state")

    def on_warp(self, s):
        cs, generation = \
            self.reference_viewer.config_state.state_and_generation
        cs = deepcopy(cs)

        cs.status_messages[self.WARP_ACTION] = \
            "Warping alignment image to reference... (patience please)"
        self.reference_viewer.config_state.set_state(
             cs, existing_generation=generation)
#        ioloop = neuroglancer.server.global_server.ioloop
#        cb = ioloop._callbacks.pop()
#        try:
#            ioloop._run_callback(cb)
#        except:
#            ioloop._callbacks.push(cb)
        try:
            self.align_image()
            with self.reference_viewer.txn() as txn:
                layer(txn, self.ALIGNMENT, self.alignment_image,
                      green_shader, 1.0, voxel_size=self.reference_voxel_size),
            self.refresh_brightness()
            self.post_message(self.reference_viewer, self.WARP_ACTION,
                    "Warping complete, thank you for your patience.")
        except:
            self.post_message(self.reference_viewer, self.WARP_ACTION,
                    "Oh my, something went wrong. See console log for details.")
            raise

    def align_image(self):
        """Warp the moving image into the reference image's space"""
        self.warper = Warper(self.reference_pts, self.moving_pts)
        inputs = [
            np.arange(0,
                      self.reference_image.shape[_]+ self.decimation - 1,
                      self.decimation)
            for _ in range(3)]
        self.warper = self.warper.approximate(*inputs)
        self.warpers[id(self)] = self.warper
        with multiprocessing.Pool(self.n_workers) as pool:
            batch_size = int(
                np.ceil(len(self.reference_image) /
                        multiprocessing.cpu_count()))
            futures = []
            for z0 in range(0, self.reference_image.shape[0], batch_size):
                z1 = min(z0+batch_size, self.reference_image.shape[0])
                futures.append(
                    pool.apply_async(warp_image,
                                     (z0, z1, id(self), self.reference_image.shape)))
            pool.close()
            for future in futures:
                future.get()

    def print_viewers(self):
        """Print the URLs of the viewers to the console"""
        print("Reference viewer: %s" % repr(self.reference_viewer))
        print("Moving viewer: %s" % repr(self.moving_viewer))

    def launch_viewers(self):
        """Launch webpages for each of the viewers"""
        webbrowser.open_new(self.reference_viewer.get_viewer_url())
        webbrowser.open_new(self.moving_viewer.get_viewer_url())


def warp_image(z0, z1, key, shape):
    warper = ViewerPair.warpers[key]
    moving_img = ViewerPair.moving_images[key]
    if key not in ViewerPair.alignment_buffers:
        alignment_raw = ViewerPair.alignment_raw[key]
        alignment_image = np.frombuffer(
                alignment_raw, np.float32, count=np.prod(shape)).reshape(shape)
        ViewerPair.alignment_buffers[key] = alignment_image
    else:
        alignment_image = ViewerPair.alignment_buffers[key]

    z, y, x = np.mgrid[z0:z1, 0:shape[1], 0:shape[2]]
    src_coords = np.column_stack([z.flatten(),
                                  y.flatten(), x.flatten()])
    ii, jj, kk = [_.reshape(z.shape) for _ in warper(src_coords).transpose()]
    map_coordinates(moving_img, [ii, jj, kk],
                    output=alignment_image[z0:z1])


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
    if args.static_content_source is not None:
        logging.warning("--static-content-source no longer has any effect")
        logging.warning("You can omit it if you want.")
    reference_voxel_size = \
        [float(_)*1 for _ in args.reference_voxel_size.split(",")]
    moving_voxel_size = \
        [float(_)*1 for _ in args.moving_voxel_size.split(",")]
    logging.info("Reading reference image")
    reference_image = tifffile.imread(args.reference_image).astype(np.float32)
    logging.info("Reading moving image")
    moving_image = tifffile.imread(args.moving_image).astype(np.float32)
    if args.segmentation is not None:
        logging.info("Reading segmentation")
        segmentation = tifffile.imread(args.segmentation).astype(np.uint32)
    else:
        segmentation = None
    vp = ViewerPair(reference_image, moving_image, segmentation, args.points,
                    reference_voxel_size, moving_voxel_size,
                    n_workers=args.n_workers)
    if not args.no_launch:
        vp.launch_viewers()
    vp.print_viewers()
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
