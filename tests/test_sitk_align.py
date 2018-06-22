import unittest
from nuggt._sitk_align import parse
import numpy as np


class Test_SitkAlign(unittest.TestCase):
    def test_parse(self):
        out_array = np.zeros((10, 3), np.float32)
        parse(np.frombuffer(example_ptsfile, np.uint8), out_array)
        np.testing.assert_almost_equal(out_array, out_pts, 5)

if __name__ == '__main__':
    unittest.main()

example_ptsfile = b"""Point	0	; InputIndex = [ 0 0 150 ]	; InputPoint = [ 0.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 18 9 146 ]	; OutputPoint = [ 18.407703 8.746117 146.331249 ]	; Deformation = [ 18.407703 8.746118 -3.668751 ]	; OutputIndexMoving = [ 18 9 146 ]
Point	1	; InputIndex = [ 1 0 150 ]	; InputPoint = [ 1.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 19 9 146 ]	; OutputPoint = [ 19.238737 8.793738 146.297835 ]	; Deformation = [ 18.238737 8.793737 -3.702165 ]	; OutputIndexMoving = [ 19 9 146 ]
Point	2	; InputIndex = [ 2 0 150 ]	; InputPoint = [ 2.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 20 9 146 ]	; OutputPoint = [ 20.068458 8.841838 146.263538 ]	; Deformation = [ 18.068459 8.841838 -3.736462 ]	; OutputIndexMoving = [ 20 9 146 ]
Point	3	; InputIndex = [ 3 0 150 ]	; InputPoint = [ 3.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 21 9 146 ]	; OutputPoint = [ 20.896961 8.890395 146.228429 ]	; Deformation = [ 17.896961 8.890395 -3.771571 ]	; OutputIndexMoving = [ 21 9 146 ]
Point	4	; InputIndex = [ 4 0 150 ]	; InputPoint = [ 4.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 22 9 146 ]	; OutputPoint = [ 21.724336 8.939386 146.192577 ]	; Deformation = [ 17.724337 8.939386 -3.807423 ]	; OutputIndexMoving = [ 22 9 146 ]
Point	5	; InputIndex = [ 5 0 150 ]	; InputPoint = [ 5.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 23 9 146 ]	; OutputPoint = [ 22.550678 8.988787 146.156050 ]	; Deformation = [ 17.550678 8.988787 -3.843950 ]	; OutputIndexMoving = [ 23 9 146 ]
Point	6	; InputIndex = [ 6 0 150 ]	; InputPoint = [ 6.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 23 9 146 ]	; OutputPoint = [ 23.376077 9.038575 146.118919 ]	; Deformation = [ 17.376078 9.038575 -3.881081 ]	; OutputIndexMoving = [ 23 9 146 ]
Point	7	; InputIndex = [ 7 0 150 ]	; InputPoint = [ 7.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 24 9 146 ]	; OutputPoint = [ 24.200627 9.088727 146.081252 ]	; Deformation = [ 17.200626 9.088727 -3.918748 ]	; OutputIndexMoving = [ 24 9 146 ]
Point	8	; InputIndex = [ 8 0 150 ]	; InputPoint = [ 8.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 25 9 146 ]	; OutputPoint = [ 25.024419 9.139219 146.043119 ]	; Deformation = [ 17.024420 9.139219 -3.956881 ]	; OutputIndexMoving = [ 25 9 146 ]
Point	9	; InputIndex = [ 9 0 150 ]	; InputPoint = [ 9.000000 0.000000 150.000000 ]	; OutputIndexFixed = [ 26 9 146 ]	; OutputPoint = [ 25.847547 9.190029 146.004590 ]	; Deformation = [ 16.847548 9.190029 -3.995410 ]	; OutputIndexMoving = [ 26 9 146 ]"""

out_pts = np.array([[18.407703, 8.746117, 146.331249],
                    [19.238737, 8.793738, 146.297835],
                    [20.068458, 8.841838, 146.263538],
                    [20.896961, 8.890395, 146.228429],
                    [21.724336, 8.939386, 146.192577],
                    [22.550678, 8.988787, 146.156050],
                    [23.376077, 9.038575, 146.118919],
                    [24.200627, 9.088727, 146.081252],
                    [25.024419, 9.139219, 146.043119],
                    [25.847547, 9.190029, 146.004590]])