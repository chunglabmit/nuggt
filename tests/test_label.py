import numpy as np
import unittest

from nuggt.label import get_segment_ids


class TestLabel(unittest.TestCase):

    def make_case(self):
        i, j, k = [_.flatten() for _ in np.mgrid[0:29:5, 0:29:5, 0:29:5]]
        segmentation = np.random.RandomState(1234).randint(
            0, 1000, size=(25, 25, 25))
        fixed_pts = np.column_stack([i, j, k])
        moving_pts = fixed_pts * 4
        return segmentation, fixed_pts, moving_pts

    def test_inside(self):
        segmentation, fixed_pts, moving_pts = self.make_case()
        lookup_pts = [[1, 5, 9]]
        result = get_segment_ids(
            segmentation, fixed_pts, moving_pts, lookup_pts)
        self.assertEqual(result[0], segmentation[0, 1, 2])

    def test_outside(self):
        segmentation, fixed_pts, moving_pts = self.make_case()
        lookup_pts = np.column_stack([
            _.flatten() for _ in np.mgrid[-3:105:53, -3:105:53, -3:105:53]
        ])
        # Get rid of 50, 50, 50
        lookup_pts = np.delete(lookup_pts, len(lookup_pts) // 2, 0)
        result = get_segment_ids(
            segmentation, fixed_pts, moving_pts, lookup_pts)
        np.testing.assert_equal(result, 0)


if __name__=="__main__":
    unittest.main()