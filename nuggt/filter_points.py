# Filter points by atlas region
import argparse
import numpy as np
import json
import sys
import multiprocessing
import tifffile
from .utils.warp import Warper
from .brain_regions import BrainRegions

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--points",
                        required=True,
                        help="The points file to filter")
    parser.add_argument("--segmentation",
                        required=True,
                        help="The atlas segmentation file, e.g. "
                        "annotation_25_whole_sagittal.tif")
    parser.add_argument("--alignment",
                        required=True,
                        help="The alignment file, for instance from "
                        "rescale-alignment-file")
    parser.add_argument("--brain-regions-file",
                        required=True,
                        help="The AllBrainRegions.csv file that has "
                        "correspondences between region IDs and names")
    parser.add_argument("--regions",
                        default="Isocortex",
                        help="The acronyms of the regions to be collected "
                        "e.g. \"CTX,CA\". This is a comma-delimited list")
    parser.add_argument("--output",
                        required=True,
                        help="The name of the output file, a json-encoded "
                        "list of points in x,y,z format.")
    parser.add_argument("--n-cores",
                        default=multiprocessing.cpu_count(),
                        type=int,
                        help="Number of cores to use when multiprocessing")
    return parser.parse_args(args)

warper_fn = None


def main(args=sys.argv[1:]):
    global warper_fn
    opts = parse_args(args)
    with open(opts.points) as fd:
        points = np.array(json.load(fd))[:, ::-1]
    with open(opts.alignment) as fd:
        alignment = json.load(fd)
    warper = Warper(src_coords = alignment["moving"],
                    dest_coords=alignment["reference"])
    warper_fn = warper.transform
    with multiprocessing.Pool(opts.n_cores) as pool:
        idx_size = int((len(points) + opts.n_cores - 1) / opts.n_cores)
        idxs = np.arange(0, len(points), idx_size)
        assert(idxs[-1] + idx_size >= len(points))
        idxs_end = np.minimum(len(points), idxs+idx_size)
        points_warped = pool.map(warper_fn,
                                 [points[s:e] for s,e in zip(idxs, idxs_end)])

    points_warped = np.concatenate(points_warped, axis=0).astype(int)
    segmentation = tifffile.imread(opts.segmentation)
    mask = np.all((points_warped >= 0) &
                  (points_warped < np.array([segmentation.shape])), 1)
    mpoints = points[mask]
    mpoints_warped = points_warped[mask]
    regions = segmentation[mpoints_warped[:, 0],
                           mpoints_warped[:, 1],
                           mpoints_warped[:, 2]]
    with open(opts.brain_regions_file) as fd:
        abr = BrainRegions.parse(fd)
    all_ids = set()
    for acronym in opts.regions.split(","):
        name = abr.get_name(abr.get_acronym_id(acronym))
        all_ids.update(abr.get_ids_for_region(name))
    in_regions = np.zeros(max(np.max(regions), max(all_ids)) + 1, bool)
    for an_id in all_ids:
        in_regions[an_id] = True
    mask = in_regions[regions]
    points_out = mpoints[mask]
    with open(opts.output, "w") as fd:
        json.dump(points_out[:, ::-1].tolist(), fd, indent=2)

if __name__ == "__main__":
    main()
