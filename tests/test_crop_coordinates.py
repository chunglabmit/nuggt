import contextlib
import json
import tempfile
import unittest
from nuggt.crop_coordinates import  main

@contextlib.contextmanager
def make_case(d):
    """Make the files for a test case

    :param d: The list of lists of points
    :return: file names of the --input and --output
    """
    with tempfile.NamedTemporaryFile(suffix=".json") as input:
        with open(input.name, "w") as fd:
            json.dump(d, fd)
        with tempfile.NamedTemporaryFile(suffix=".json") as output:
            yield input.name, output.name


class TestCropCoordinates(unittest.TestCase):
    def test_everything(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case, result)

    def json_load(self, output):
        with open(output) as fd:
            return json.load(fd)

    def test_x0(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--x0", "4"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[1:], result)

    def test_x1(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--x1", "4"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[:1], result)

    def test_y0(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--y0", "5"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[1:], result)

    def test_y1(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--y1", "5"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[:1], result)

    def test_z0(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--z0", "6"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[1:], result)

    def test_z1(self):
        my_case = [[1, 2, 3], [4, 5, 6]]
        with make_case(my_case) as (input, output):
            main(["--input", input,
                  "--output", output,
                  "--z1", "6"])
            result = self.json_load(output)
            self.assertSequenceEqual(my_case[:1], result)


if __name__ == '__main__':
    unittest.main()
