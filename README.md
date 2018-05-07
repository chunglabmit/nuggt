#NeUroGlancer Ground-Truth: nuggt

This script uses Neuroglancer to collect
cell center ground truth for a 3-d cell
segmentation.

Usage:

Compile Neuroglancer according to the directions
[here](https://github.com/google/neuroglancer/blob/master/README.md)
and [here](https://github.com/google/neuroglancer/blob/master/python/README.md)

Start the static content server:
```bash
> npm run dev-server
```

Install *nuggt* like this:

```
> git clone https://github.com/chunglabmit/nuggt
> cd nuggt
> pip install nuggt
```

Run *nuggt* like this:
```
> nuggt --image <image-file> --output <points-json-file> [--min-distance <d>]
```
where
* *image-file* is the path to a .tif stack file
* *points-json-file* is the path to the points.json file where the
  voxel coordinates selected by the user are stored
* *d* is the minimum allowed distance in voxels between entered points

Commands available in the browser:
* *t key* - add a point at the current cursor (easiest to place cursor over
            the x-y, x-z or y-z displays to pick the point in 2-d)
* *u key* - save the points to *points.json*
* *v key* - delete the point nearest to the cursor

## nuggt-align

Align images using Neuroglancer.

**nuggt-align** is a command-line program that starts two neuroglancer
instances, one for a *moving image* and one for a *reference image*. The
purpose of the program is to establish common points of reference in each
image which can be used to warp the *moving image* onto the *reference image*.

Run **nuggt-align** like this:
```bash
> nuggt-align --moving-image <moving-image-file> \
              --reference-image <reference-image-file> \
              --points <points-file> \
              [--no-launch]
```
where:
* **moving-image-file** is a 3D .tiff file containing the volume of the
image to be aligned to the reference image
* **reference-image-file** is a 3D .tiff file containing the volume of
the reference image, in the reference coordinate frame.
* **points-file** is a file to contain (or already containing) the
moving image reference points and their corresponding points in the 
reference image. **nuggt-align** initially loads the points from this file
if it exists and, when you save, it overwrites this file with the current
list of points.
* **--no-launch** if you want to start **nuggt-align** without
automatically creating new browser windows with the moving and
reference images.

**nuggt-align** will print the URLs of the reference viewer and moving
viewer on startup. These can be used to launch browser instances for
editing.

**nuggt-align** works by maintaining a list of point annotations
for each image in the *correspondence-points* annotation layer. It
maintains one pair of points in the *edit* annotation layer. These are
the points currently being edited. The following commands control the
edit process:

* *control-mouse-button0* (typically left mouse button) - place an edit point
* *shift-e* - edit the currently selected point (move currently selected point
from the correspondence-points annotation layer to the edit layer).
* *shift-d* - done with the point currently being edited. This moves the
point in the edit annotation layer in the reference and moving views to the
correspondence-points layer.
* *shift-c* - clear. Clears edit points from the edit annotation layer
* *shift-n* - saves the point being edited and moves to the next point in
the correspondence-points annotation layer.
* *shift-p* - saves the point being edited and moves to the previous point
in the correspondence-points annotation layer.
* *shift-t* - transform. This places or moves the point in the edit annotation
layer in the moving view at the location that corresponds to the point in the
edit annotation layer in the reference view (according to the last warping
transform). You can place a point in the reference view, press *shift-t*, and
then see and edit its location in the moving view to correct the warp.
* *shift-w* - warp the moving layer's image to the reference layer using the
point correspondences.

## SITK-ALIGN

**sitk-align** aligns a moving image to a reference image based on work
done by Jae Cho to adapt SimpleElastix / SimpleITK to mouse brain images. The
application can both produce an aligned image and, more importantly, it can
take a set of reference points, stored in a JSON file and convert these to a
point file for **nuggt-align**.

### Installation

SimpleElastix has a non-standard installation procedure because it is primarily
a C++ application with Python bindings. It should be installed following
the [super build](https://github.com/SuperElastix/SimpleElastix#building-with-the-superbuild)
instructions. One installation method might be to create and activate an
Anaconda environment, pip install Nuggt, then run the superbuild in the
activated environment. Nuggt has been tested with SimpleElastix git hash
[9dfa8cb](https://github.com/SuperElastix/SimpleElastix/tree/9dfa8cb7c99e78b36f64bb6600b084b70960f166).

### Invocation

Invoke **sitk-align** like this:

```commandline
> sitk-align --moving-file <moving-file> --fixed-file <fixed-file> \
             [--fixed-point-file <fixed-point-file>] \
             [--alignment-point-file <alignment-point-file>] \
             [--aligned-file <aligned-file]\

```
where
* *moving-file* is the path to the moving 3-d image. See SimpleITK for accepted
formats *(hint - 3D tif works)*.
* *fixed-file* is the path to the fixed or reference 3-d image.
* *fixed-point-file* is the optional .json file of reference points in the
reference image's space. These will be converted to points in the moving-file's
space. The format is a list of lists with the inner list being the Z, Y and X
coordinates of the point, in that order.
* *alignment-point-file* is the optional .json file to be written. This file
will be in the format used by the *--points-file* argument of **nuggt-align**.
* *aligned-file* is the optional file name for the moving file, warped into the
fixed-point-file's space. The file will not be written if the switch is not
specified.
