import numpy as np
import unittest
from nuggt.utils.ngutils import soft_max_brightness


class TestNGUtils(unittest.TestCase):
    def test_soft_max_brightness(self):
        img = np.arange(1000).reshape(10, 10, 10).astype(np.float32) / 1000
        self.assertAlmostEqual(.998, soft_max_brightness(img), 5)

    def test_soft_max_brightness_lots_of_zeros(self):
        img = np.zeros((100, 100, 100))
        img[0, 0, 0] = .5
        self.assertAlmostEqual(.5, soft_max_brightness(img), 5)

    def test_soft_max_brightness_all_zeros(self):
        img = np.zeros((10, 10, 10))
        self.assertGreater(soft_max_brightness(img), 0)


if __name__ == '__main__':
    unittest.main()
