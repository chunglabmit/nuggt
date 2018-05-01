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

*control-mouse-button0* (typically left mouse button) - 
