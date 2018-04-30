"""Warp images

"""

import numpy as np
from scipy.interpolate import Rbf, RegularGridInterpolator


class Warper:
    """Warp arbitrary points in one ND space to another

    Use an array of Rbfs to warp one space to another.
    """
    def __init__(self, src_coords,
                 dest_coords,
                 function="thin_plate",
                 epsilon=None,
                 smooth=None,
                 norm = None):
        """Constructor

        :param src_coords: an N x M array of coordinates in the space to be
        warped where "M" is the dimension of the coordinate space.
        :param dest_coords: an N x M' array of coordinates in the target space.
        Note that the destination space is allowed to be of different dimension
        than the source.
        :param function: the radial basis function (see scipy.interpolate.Rbf).
        The default, unlike Rbf, is "thin_plate" for thin-plate splines.
        :param epsilon: Adjustable constant if required by the radial basis
        function (see scipy.interpolate.Rbf)
        :param smooth: Smoothing factor. Zero means always go through each node
        Defaults to zero.
        :param norm: A function that computes the distance between two points.
        Defaults to Euclidean.
        """
        kwds = dict([(k, v) for k, v in (
            ("function", function),
            ("epsilon", epsilon),
            ("smooth", smooth),
            ("norm", norm)
        ) if v is not None])
        src_coords = np.atleast_2d(src_coords)
        self.input_dim = src_coords.shape[1]
        dest_coords = np.atleast_2d(dest_coords)
        self.output_dim = dest_coords.shape[1]
        src_args = [src_coords[:, _] for _ in range(self.input_dim)]
        self.rbfs = [
            Rbf(*tuple(src_args + [dest_coords[:, _]]), **kwds)
            for _ in range(self.output_dim)
        ]

    def approximate(self, *args):
        """Create an alternative warper based on cubic splines

        For computational efficiency, compute a set of multivariate splines
        on a hyper-rectangular grid that approximate the warping.

        :param args: one array per source dimension giving the nodes of the
                     grid in ascending order.
        :returns: a function that can be used to transform
        to the destination space, valid between the first and last coordinates
        specified in the grid.
        """
        assert len(args) == self.input_dim
        slices = tuple([slice(0, len(arg)) for arg in args])
        grid = np.mgrid[slices]
        gshape = grid.shape[1:]
        arrays = [
            rbf(*tuple([arg[grid[in_idx].flatten()]
                        for in_idx, arg in enumerate(args)])).reshape(gshape)
            for rbf in self.rbfs]

        interpolators = [RegularGridInterpolator(args, array)
                         for array in arrays]

        def warp_function(*src_coords):
            """Warp source coordinates to destination
            
            :param src_coords: an NxM array of source coordinates
            :param dest_coords: an NxM' array of destination coordinates,
            approximated by the gridding of the warper
            """
            src_coords = np.atleast_2d(src_coords)
            return np.column_stack([interpolator(src_coords).flatten()
                                    for interpolator in interpolators])
        return warp_function

    def __call__(self, src_coords):
        """Transform source coordinates to destination"""
        return self.transform(src_coords)

    def transform(self, src_coords):
        """Transform source coordinates to destination

        :param src_coords:
        """
        src_coords = np.atleast_2d(src_coords)
        return np.column_stack([
            rbf(*src_coords.transpose()) for rbf in self.rbfs])
