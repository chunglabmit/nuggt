import contextlib
import json
import numpy as np
import os
import shutil
import tempfile
import tifffile
import unittest

from nuggt.calculate_intensity_in_regions import do_plane, main
from nuggt.utils.warp import Warper


class FakeSharedMemory:

    def __init__(self, a):
        self.a = a

    @contextlib.contextmanager
    def txn(self):
        yield self.a

    @property
    def shape(self):
        return self.a.shape


@contextlib.contextmanager
def make_plane(a):
    with tempfile.NamedTemporaryFile(suffix=".tiff") as tf:
        tifffile.imsave(tf.name, a)
        yield tf.name


class TestDoPlane(unittest.TestCase):
    def test_nothing(self):
        xform = Warper(np.array([[10, 0, 0],
                                 [10, 10, 0],
                                 [10, 0, 10],
                                 [10, 10, 10],
                                 [15, 5, 5],
                                 [20, 0, 0],
                                 [20, 10, 0],
                                 [20, 0, 10],
                                 [20, 10, 10]]),
                       np.array([[0, 0, 0],
                                 [0, 10, 0],
                                 [0, 0, 10],
                                 [0, 10, 10],
                                 [5, 5, 5],
                                 [10, 0, 0],
                                 [10, 10, 0],
                                 [10, 0, 10],
                                 [10, 10, 10]]))
        seg = np.ones((10, 10, 10), np.uint32)
        with make_plane(np.ones((10, 10), np.uint16) * 2) as plane_path:
            c, s = do_plane(plane_path, 0, FakeSharedMemory(seg),
                            xform, grid_size=10)
        self.assertEqual(len(c), 2)
        self.assertEqual(c[0], 100)
        self.assertEqual(c[1], 0)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0],  200)
        self.assertEqual(s[1], 0)

    def test_simple(self):
        xform = Warper(np.array([[0, 0, 0],
                                 [0, 10, 0],
                                 [0, 0, 10],
                                 [0, 10, 10],
                                 [5, 3, 3],
                                 [5, 7, 7],
                                 [10, 0, 0],
                                 [10, 10, 0],
                                 [10, 0, 10],
                                 [10, 10, 10]]),
                       np.array([[0, 0, 0],
                                 [0, 10, 0],
                                 [0, 0, 10],
                                 [0, 10, 10],
                                 [5, 3, 3],
                                 [5, 7, 7],
                                 [10, 0, 0],
                                 [10, 10, 0],
                                 [10, 0, 10],
                                 [10, 10, 10]]))
        seg = np.zeros((10, 10, 10), np.uint32)
        seg[5, 3, 3] = 1
        seg[5, 7, 7] = 2
        img = np.random.RandomState(1234).randint(1, 65535, (10, 10))
        with make_plane(img.astype(np.uint16)) as plane_path:
            c, s = do_plane(plane_path, 5, FakeSharedMemory(seg),
                            xform, grid_size=10)
        self.assertEqual(len(c), 3)
        self.assertEqual(c[0], 98)
        self.assertEqual(c[1], 1)
        self.assertEqual(c[2], 1)
        self.assertEqual(len(s), 3)
        self.assertEqual(s[1],  img[3, 3])
        self.assertEqual(s[2], img[7, 7])


@contextlib.contextmanager
def named_temporary_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


class TestMain(unittest.TestCase):
    def test_level_7(self):
        with named_temporary_dir() as img_path, \
             tempfile.NamedTemporaryFile(suffix=".tiff") as seg_path, \
             tempfile.NamedTemporaryFile(suffix=".json") as align_path, \
             tempfile.NamedTemporaryFile(suffix=".csv") as brain_regions_path, \
             tempfile.NamedTemporaryFile(suffix=".csv") as out_path:
            img = np.random.RandomState(1234).randint(1, 65535, (10, 10, 10))
            for i in range(10):
                tifffile.imsave(os.path.join(img_path, "img_%04d.tiff" % i),
                                img[i])
            seg = np.zeros((10, 10, 10), np.uint16)
            seg[5, 3, 3] = 1
            seg[5, 7, 7] = 2
            tifffile.imsave(seg_path.name, seg)
            xform = [[0, 0, 0],
                     [0, 10, 0],
                     [0, 0, 10],
                     [0, 10, 10],
                     [5, 3, 3],
                     [5, 7, 7],
                     [10, 0, 0],
                     [10, 10, 0],
                     [10, 0, 10],
                     [10, 10, 10]]
            with open(brain_regions_path.name, "w") as fd:
                fd.write('id,counts,density,name,acronym\n')
                fd.write("0,98,98,b'background',b'background',b'background',"
                         "b'background',b'background',b'background',"
                         "b'background'\n")
                fd.write("1,1,1,b'region_1',b'foreground',b'foreground',"
                         "b'foreground',b'foreground',b'foreground',"
                         "b'foreground'\n")
                fd.write("2,1,1,b'region_2',b'foreground',b'foreground',"
                         "b'foreground',b'foreground',b'foreground',"
                         "b'foreground'\n")
            with open(align_path.name, "w") as fd:
                json.dump(dict(moving=xform, reference=xform), fd)
            main(["--input", os.path.join(img_path, "img_*.tiff",),
                  "--alignment", align_path.name,
                  "--reference-segmentation", seg_path.name,
                  "--brain-regions-csv", brain_regions_path.name,
                  "--output", out_path.name,
                  "--level", "7"])
            with open(out_path.name, "r") as fd:
                header = fd.readline()
                line_0 = fd.readline().split(",")
                line_1 = fd.readline().split(",")
                line_2 = fd.readline().split(",")
            self.assertEqual(line_0[0], "0")
            self.assertEqual(line_0[2], "998")
            self.assertAlmostEqual(float(line_0[4]), int(line_0[3]) / 998, 0)
            self.assertEqual(line_1[0], "1")
            self.assertEqual(line_1[1][1:-1], "region_1")
            self.assertEqual(line_1[2], "1")
            self.assertEqual(int(line_1[3]), img[5, 3, 3])
            self.assertEqual(float(line_1[4]), img[5, 3, 3])
            self.assertEqual(line_2[0], "2")
            self.assertEqual(line_2[1][1:-1], "region_2")
            self.assertEqual(line_2[2], "1")
            self.assertEqual(int(line_2[3]), img[5, 7, 7])
            self.assertEqual(float(line_2[4]), img[5, 7, 7])

    def test_level_5(self):
        with named_temporary_dir() as img_path, \
             tempfile.NamedTemporaryFile(suffix=".tiff") as seg_path, \
             tempfile.NamedTemporaryFile(suffix=".json") as align_path, \
             tempfile.NamedTemporaryFile(suffix=".csv") as brain_regions_path, \
             tempfile.NamedTemporaryFile(suffix=".csv") as out_path:
            img = np.random.RandomState(1234).randint(1, 65535, (10, 10, 10))
            for i in range(10):
                tifffile.imsave(os.path.join(img_path, "img_%04d.tiff" % i),
                                img[i])
            seg = np.zeros((10, 10, 10), np.uint16)
            seg[5, 3, 3] = 1
            seg[5, 7, 7] = 2
            tifffile.imsave(seg_path.name, seg)
            xform = [[0, 0, 0],
                     [0, 10, 0],
                     [0, 0, 10],
                     [0, 10, 10],
                     [5, 3, 3],
                     [5, 7, 7],
                     [10, 0, 0],
                     [10, 10, 0],
                     [10, 0, 10],
                     [10, 10, 10]]
            with open(brain_regions_path.name, "w") as fd:
                fd.write('id,counts,density,name,acronym\n')
                fd.write("0,98,98,b'background',b'background',b'background',"
                         "b'background',b'background',b'background',"
                         "b'background'\n")
                fd.write("1,1,1,b'region_1',b'foreground',b'foreground',"
                         "b'foreground',b'foreground',b'foreground',"
                         "b'foreground'\n")
                fd.write("2,1,1,b'region_2',b'foreground',b'foreground',"
                         "b'foreground',b'foreground',b'foreground',"
                         "b'foreground'\n")
            with open(align_path.name, "w") as fd:
                json.dump(dict(moving=xform, reference=xform), fd)
            main(["--input", os.path.join(img_path, "img_*.tiff",),
                  "--alignment", align_path.name,
                  "--reference-segmentation", seg_path.name,
                  "--brain-regions-csv", brain_regions_path.name,
                  "--output", out_path.name,
                  "--level", "5"])
            with open(out_path.name, "r") as fd:
                header = fd.readline()
                line_0 = fd.readline().split(",")
                line_1 = fd.readline().split(",")
            self.assertEqual(line_0[0][1:-1], "background")
            self.assertEqual(line_0[1], "998")
            self.assertAlmostEqual(float(line_0[3]), int(line_0[2]) / 998, 0)
            self.assertEqual(line_1[0][1:-1], "foreground")
            self.assertEqual(line_1[1], "2")
            self.assertEqual(int(line_1[2]), img[5, 3, 3] + img[5, 7, 7])
            self.assertEqual(
                float(line_1[3]), (img[5, 3, 3] + img[5, 7, 7]) / 2)


if __name__ == '__main__':
    unittest.main()
