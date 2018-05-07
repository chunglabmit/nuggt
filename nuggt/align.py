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
    parser.add_argument("--reference-voxel-size",
                        help="X, Y and Z size of voxels, separated by "
                        "commas, e.g. \"1.6,1.6,1.0\"",
                        default="1.0,1.0,1.0")
    parser.add_argument("--moving-voxel-size",
                        help="X, Y and Z size of voxels, separated by "
                        "commas, e.g. \"1.6,1.6,1.0\"",
                        default="1.0,1.0,1.0")
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

    ANNOTATE_ACTION = "annotate"
    CLEAR_ACTION = "clear"
    DONE_ACTION = "done-with-point"
    EDIT_ACTION = "edit"
    NEXT_ACTION = "next"
    PREVIOUS_ACTION = "previous"
    REDO_ACTION = "redo"
    SAVE_ACTION = "save-points"
    TRANSLATE_ACTION = "translate-point"
    UNDO_ACTION = "undo"
    WARP_ACTION = "warp"

    CLEAR_KEY = "shift+keyc"
    DONE_KEY = "shift+keyd"
    EDIT_KEY = "shift+keye"
    NEXT_KEY = "shift+keyn"
    PREVIOUS_KEY = "shift+keyp"
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
  emitRGB(vec3(toNormalized(getDataValue()), 0, 
               toNormalized(getDataValue())));
}
        """

    IMAGE_SHADER="""
void main() {
  emitGrayscale(toNormalized(getDataValue()));
}
"""

    def __init__(self, reference_image, moving_image, points_file,
                 reference_voxel_size, moving_voxel_size):
        """Constructor

        :param reference_image: align to this image
        :param moving_image: align this image
        :param points_file: where to load and store points
        :param reference_voxel_size: a 3-tuple giving the X, Y and Z voxel
        size in nanometers.
        :param moving_voxel_size: the voxel size for the moving image
        """
        self.reference_image = reference_image
        self.moving_image = moving_image
        self.decimation = max(1, np.min(reference_image.shape) // 5)
        self.alignment_image = np.zeros(self.reference_image.shape,
                                        np.float32)
        self.reference_viewer = neuroglancer.Viewer()
        self.moving_viewer = neuroglancer.Viewer()
        self.points_file = points_file
        self.warper = None
        self.reference_voxel_size = reference_voxel_size
        self.moving_voxel_size = moving_voxel_size
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
        self.undo_stack = []
        self.redo_stack = []
        self.selection_index = len(self.reference_pts)
        self.update_after_edit()

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
            s.voxel_size = self.reference_voxel_size
            s.layers[self.REFERENCE] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(
                    self.reference_image,
                    voxel_size=s.voxel_size),
                shader=self.REFERENCE_SHADER
            )
            s.layers[self.ALIGNMENT] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(
                    self.alignment_image,
                    voxel_size=s.voxel_size),
                shader = self.ALIGNMENT_SHADER
            )
        self.init_actions(self.reference_viewer,
                          self.on_reference_annotate)

    def init_actions(self, viewer, on_annotate):
        """Initialize the actions for a viewer

        :param viewer: the reference or moving viewer
        :param on_edit: the function to execute when the user wants to edit
        """
        viewer.actions.add(self.ANNOTATE_ACTION, on_annotate)
        viewer.actions.add(self.CLEAR_ACTION, self.on_clear)
        viewer.actions.add(self.DONE_ACTION, self.on_done)
        viewer.actions.add(self.EDIT_ACTION, self.on_edit)
        viewer.actions.add(self.NEXT_ACTION, self.on_next)
        viewer.actions.add(self.PREVIOUS_ACTION, self.on_previous)
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
            bindings_viewer[self.CLEAR_KEY] = self.CLEAR_ACTION
            bindings_viewer[self.DONE_KEY] = self.DONE_ACTION
            bindings_viewer[self.EDIT_KEY] = self.EDIT_ACTION
            bindings_viewer[self.NEXT_KEY] = self.NEXT_ACTION
            bindings_viewer[self.PREVIOUS_KEY] = self.PREVIOUS_ACTION
            bindings_viewer[self.SAVE_KEY] = self.SAVE_ACTION
            bindings_viewer[self.REDO_KEY] = self.REDO_ACTION
            bindings_viewer[self.UNDO_KEY] = self.UNDO_ACTION
            bindings_viewer[self.WARP_KEY] = self.WARP_ACTION
            if viewer == self.reference_viewer:
                bindings_viewer[self.TRANSLATE_KEY] = self.TRANSLATE_ACTION

    def init_moving_state(self):
        """Initialize the state of the moving viewer"""
        with self.moving_viewer.txn() as s:
            s.voxel_size = self.moving_voxel_size
            s.layers[self.IMAGE] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(
                    self.moving_image,
                    voxel_size=s.voxel_size),
                shader=self.IMAGE_SHADER
            )
        self.init_actions(self.moving_viewer, self.on_moving_annotate)

    def on_reference_annotate(self, s):
        """Handle an edit in the reference viewer

        :param s: the current state
        """
        point = s.mouse_voxel_coordinates
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
        msg = "Edit point: %d %d %d" %  tuple(point.tolist())
        self.post_message(self.moving_viewer, self.EDIT, msg)

        with self.moving_viewer.txn() as txn:
            layer = neuroglancer.PointAnnotationLayer(
                points=[point.tolist()],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.layers[self.EDIT] = layer

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
            txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                points=[reference[::-1]],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.position.voxel_coordinates = reference[::-1]
        with self.moving_viewer.txn() as txn:
            txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                points=[moving[::-1]],
                annotation_color=self.EDIT_ANNOTATION_COLOR)
            txn.position.voxel_coordinates = moving[::-1]

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
        return ma[0].point[::-1].tolist()

    def get_reference_edit_point(self):
        """Get the current edit point in the reference frame"""
        try:
            ra = self.reference_viewer.state.layers[self.EDIT].annotations
        except AttributeError:
            ra = self.reference_viewer.state.layers[self.EDIT].points
        if len(ra) == 0:
            return None
        return ra[0].point[::-1].tolist()

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
                          "removed point at %d, %d, %d" %
                          tuple(reference_point[::-1]))
        moving_point = self.moving_pts.pop(idx)
        self.post_message(self.moving_viewer, self.EDIT,
                          "removed point at %d, %d, %d" %
                          tuple(moving_point[::-1]))
        entry = (self.add_point, (idx, reference_point, moving_point,
                                  not add_to_undo))
        if add_to_undo:
            self.undo_stack.append(entry)
        else:
            self.redo_stack.append(entry)
        self.update_after_edit()
        return reference_point, moving_point

    def update_after_edit(self):
        for viewer, points in ((self.reference_viewer,
                                self.annotation_reference_pts),
                               (self.moving_viewer,
                                self.annotation_moving_pts)):
            with viewer.txn() as txn:
                layer = txn.layers[self.CORRESPONDENCE_POINTS]
                txn.layers[self.CORRESPONDENCE_POINTS] = \
                    neuroglancer.PointAnnotationLayer(points=points)
                txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                    annotation_color=self.EDIT_ANNOTATION_COLOR)

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
            mp = self.warper(np.atleast_2d(rp))[0][::-1]
            with self.moving_viewer.txn() as txn:
                txn.layers[self.EDIT] = neuroglancer.PointAnnotationLayer(
                    points=[mp],
                    annotation_color=self.EDIT_ANNOTATION_COLOR)
                txn.position.voxel_coordinates = mp

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
        ioloop = neuroglancer.server.global_server.ioloop
        cb = ioloop._callbacks.pop()
        try:
            ioloop._run_callback(cb)
        except:
            ioloop._callbacks.push(cb)
        try:
            self.align_image()
            with self.reference_viewer.txn() as txn:
                txn.voxel_size = self.reference_voxel_size
                txn.layers[self.ALIGNMENT] = neuroglancer.ImageLayer(
                    source=neuroglancer.LocalVolume(
                        self.alignment_image,
                        voxel_size=txn.voxel_size),
                    shader=self.ALIGNMENT_SHADER
                )
            self.post_message(self.reference_viewer, self.WARP_ACTION,
                    "Warping complete, thank you for your patience.")
        except:
            self.post_message(self.reference_viewer, self.WARP_ACTION,
                    "Oh my, something went wrong. See console log for details.")
            raise

    def align_image(self):
        """Warp the moving image into the reference image's space"""
        warper = Warper(self.reference_pts, self.moving_pts)
        inputs = [np.arange(0, self.reference_image.shape[_]+ self.decimation - 1,
                            self.decimation) for _ in range(3)]
        self.warper = warper.approximate(*inputs)
        src_coords = np.column_stack([_.flatten() for _ in np.mgrid[
                        0:self.reference_image.shape[0],
                        0:self.reference_image.shape[1],
                        0:self.reference_image.shape[2]]])
        ii, jj, kk = [_.reshape(self.reference_image.shape) for _ in
                      self.warper(src_coords).transpose()]
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
    reference_voxel_size = \
        [float(_)*1000 for _ in args.reference_voxel_size.split(",")]
    moving_voxel_size = \
        [float(_)*1000 for _ in args.moving_voxel_size.split(",")]
    logging.info("Reading reference image")
    reference_image = normalize_image(tifffile.imread(args.reference_image))
    logging.info("Reading moving image")
    moving_image = normalize_image(tifffile.imread(args.moving_image))
    vp = ViewerPair(reference_image, moving_image, args.points,
                    reference_voxel_size, moving_voxel_size)
    if not args.no_launch:
        vp.launch_viewers()
    vp.print_viewers()
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
