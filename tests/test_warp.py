import unittest
import numpy as np
from nuggt.utils.warp import Warper


class TestWarp(unittest.TestCase):
    def test_3D(self):
        i, j, k = np.mgrid[0:10, 0:10, 0:10].astype(np.float32)

        def fii(i, j, k):
            return i ** 2 + j * 4.5 + np.sqrt(k)

        def fjj(i, j, k):
            return i * k + j ** 3

        def fkk(i, j, k):
            return i * j * k

        ii, jj, kk = [_(i, j, k) for _ in (fii, fjj, fkk)]
        warper = Warper(
            np.column_stack([i.flatten(), j.flatten(), k.flatten()]),
            np.column_stack([ii.flatten(), jj.flatten(), kk.flatten()]))
        r = np.random.RandomState(1234)
        iin, jin, kin = [r.uniform(0, 9, 10) for _ in range(3)]
        result = warper(np.column_stack([iin, jin, kin]))
        for iiin, jjin, kkin, (iout, jout, kout) in zip(iin, jin, kin, result):
            floor_i = int(np.floor(iiin))
            floor_j = int(np.floor(jjin))
            floor_k = int(np.floor(kkin))
            ceil_i = int(np.ceil(iiin))
            ceil_j = int(np.ceil(jjin))
            ceil_k = int(np.ceil(kkin))
            min_i, min_j, min_k = [min(_[floor_i, floor_j, floor_k],
                                       _[ceil_i, ceil_j, ceil_k])
                                   for _ in (ii, jj, kk)]
            max_i, max_j, max_k = [max(_[floor_i, floor_j, floor_k],
                                       _[ceil_i, ceil_j, ceil_k])
                                   for _ in (ii, jj, kk)]
            self.assertLessEqual(min_i, iout)
            self.assertGreaterEqual(max_i, iout)
            self.assertLessEqual(min_j, jout)
            self.assertGreaterEqual(max_j, jout)
            self.assertLessEqual(min_k, kout)
            self.assertGreaterEqual(max_k, kout)

    def test_approximate(self):
        i, j, k = np.mgrid[0:10, 0:10, 0:10].astype(np.float32)

        def fii(i, j, k):
            return i ** 2 + j * 4.5 + np.sqrt(k)

        def fjj(i, j, k):
            return i * k + j ** 3

        def fkk(i, j, k):
            return i * j * k

        ii, jj, kk = [_(i, j, k) for _ in (fii, fjj, fkk)]
        warper = Warper(
            np.column_stack([i.flatten(), j.flatten(), k.flatten()]),
            np.column_stack([ii.flatten(), jj.flatten(), kk.flatten()]))
        warper = warper.approximate(*[np.arange(0, 10, 2)] * 3)
        r = np.random.RandomState(1234)
        iin, jin, kin = [r.randint(0, 8, 10) + .5 for _ in range(3)]
        result = warper(np.column_stack([iin, jin, kin]))
        for iiin, jjin, kkin, (iout, jout, kout) in zip(iin, jin, kin, result):
            floor_i = int(np.floor(iiin))
            floor_j = int(np.floor(jjin))
            floor_k = int(np.floor(kkin))
            ceil_i = int(np.ceil(iiin))
            ceil_j = int(np.ceil(jjin))
            ceil_k = int(np.ceil(kkin))
            min_i, min_j, min_k = [min(_[floor_i, floor_j, floor_k],
                                       _[ceil_i, ceil_j, ceil_k])
                                   for _ in (ii, jj, kk)]
            max_i, max_j, max_k = [max(_[floor_i, floor_j, floor_k],
                                       _[ceil_i, ceil_j, ceil_k])
                                   for _ in (ii, jj, kk)]
            self.assertLessEqual(min_i, iout)
            self.assertGreaterEqual(max_i, iout)
            self.assertLessEqual(min_j, jout)
            self.assertGreaterEqual(max_j, jout)
            self.assertLessEqual(min_k, kout)
            self.assertGreaterEqual(max_k, kout)

if __name__ == '__main__':
    unittest.main()
