"""Look up labels for a segmentation

This uses the structure for the Allen Brain Atlas to find the labels associated
with a reference segmentation for a list of points
"""
import numpy as np

from .utils.warp import Warper


def get_segment_ids(segmentation, fixed_pts, moving_pts, lookup_pts,
                    warp_args={}, decimation=None):
    """Find the segment ID for every point in lookup_pts

    :param segmentation: a reference segmentation in the fixed space
    :param fixed_pts: keypoints in the fixed space
    :param moving_pts: corresponding keypoints in the moving space
    :param lookup_pts: look up the segment IDs for these points
    :param warp_args: keyword arguments for the warper (see nuggt.warp.Warper)
    :param decimation: downsample the fixed segmentation by this amount
    when creating the cubic splines from the thin-plate ones. Defaults
    to breaking the destination space into at least 5 blocks in each direction.
    :returns: a vector of segment ID per lookup point
    """
    if decimation is None:
        decimation = max(1, np.min(segmentation.shape) // 5)
    inputs = [
        np.arange(0,
                  segmentation.shape[_] + decimation - 1,
                  decimation)
        for _ in range(3)]

    warper = Warper(moving_pts, fixed_pts, *warp_args).approximate(*inputs)
    return get_segment_ids_using_warper(segmentation, warper, lookup_pts)


def get_segment_ids_using_warper(segmentation, warper, lookup_pts):
    """Get segment IDs per lookup point, giving a transform function

    :param segmentation: the segmentation in the reference space
    :param warper: a function object that can be called with a list of
    lookup points to return their location in the reference space
    :param lookup_pts: look up the segment IDs for these points
    :returns: a vector of segment ID per lookup point
    """
    reference_pts = np.round(warper(lookup_pts), 0).astype(np.int32)
    result = np.zeros(len(reference_pts), segmentation.dtype)
    mask = \
        (~ np.any(np.isnan(reference_pts), 1)) &\
        np.all(reference_pts >= 0, 1) &\
        (reference_pts[:, 0] < segmentation.shape[0]) &\
        (reference_pts[:, 1] < segmentation.shape[1]) &\
        (reference_pts[:, 2] < segmentation.shape[2])
    result[mask] = segmentation[reference_pts[mask, 0],
                                reference_pts[mask, 1],
                                reference_pts[mask, 2]]
    return result


