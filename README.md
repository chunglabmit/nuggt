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
