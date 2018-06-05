"""ngreference - a class for displaying the reference image in neuroglancer


"""
import abc
import neuroglancer
import json
import tifffile

from .utils.warp import Warper
from .utils.ngutils import *


class NGReference(abc.ABC):

    def __init__(self, ref_img, ref_seg, moving_pts, ref_pts, moving_shape):
        self.viewer = neuroglancer.Viewer()

        za = np.linspace(0, moving_shape[0], 10)
        ya = np.linspace(0, moving_shape[1], 10)
        xa = np.linspace(0, moving_shape[2], 10)
        self.warp_to_ref = Warper(moving_pts, ref_pts).approximate(za, ya, xa)
        za = np.linspace(0, ref_img.shape[0], 10)
        ya = np.linspace(0, ref_img.shape[1], 10)
        xa = np.linspace(0, ref_img.shape[2] , 10)
        self.warp_to_moving = \
            Warper(ref_pts, moving_pts).approximate(za, ya, xa)

        with self.viewer.txn() as txn:
            layer(txn, "image", ref_img, gray_shader, 1.0)
            seglayer(txn, "segmentation", ref_seg)

    def add_points(self, points, layer_name="annotation", layer_color="yellow"):
        """Add a point annotation layer to the viewer

        :param points: Points in the moving space
        :param layer_name: the annotation's name in Neuroglancer
        :param layer_color: the color for the annotation dots
        """
        rpoints = self.warp_to_ref(points)
        with self.viewer.txn() as txn:
            pointlayer(txn, layer_name,
                       rpoints[:, 2], rpoints[:, 1], rpoints[:, 0],
                       layer_color)

    def on_action(self, s):
        point = s.mouse_voxel_coordinates
        moving_point = self.warp_to_moving(point[::-1].reshape(1, 3)).reshape(3)
        self.action_handler(s, moving_point)

    @abc.abstractmethod
    def action_handler(self, s, moving_point):
        """Handle an action - override in derived class

        :param s: the state at the time of the action
        :param moving_point: the location of the cursor in the moving reference
        frame
        """
        raise NotImplementedError()