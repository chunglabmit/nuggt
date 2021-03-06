# -*- coding: utf-8 -*-
import argparse
from functools import reduce
import json
import matplotlib.cm
import numpy as np
import pandas
import tifffile
import xml.etree.ElementTree as ET
from urllib.request import urlopen

RGB_2_ACR_URL = "https://scalablebrainatlas.incf.org/templates/ABA_v3/template/rgb2acr.json"
PATH_TAG = "{http://www.w3.org/2000/svg}path"
RECT_TAG = "{http://www.w3.org/2000/svg}rect"
STYLE_TAG = "{http://www.w3.org/2000/svg}style"
TEXT_TAG = "{http://www.w3.org/2000/svg}text"


def parse_args():
    parser = argparse.ArgumentParser(
        description="A program to convert the output of count-points-in-region "
        "to an .SVG brain map graphic."
    )
    parser.add_argument(
        "--svg-file",
        required=True,
        help="The SVG of the section to be colored. Download these from here: "
             "https://scalablebrainatlas.incf.org/mouse/ABA_v3#downloads")
    parser.add_argument(
        "--count-file",
        action="append",
        help="The count file generated by count-points-in-region. May be "
             "specified multiple times to include counts from different "
             "levels.")
    parser.add_argument(
        "--brain-regions-file",
        required=True,
        help="The AllBrainRegions.csv file giving the correspondence between "
             "names and IDs")
    parser.add_argument(
        "--output",
        required=True,
        help="The name of the SVG output file")
    parser.add_argument(
        "--rgb2acr-file",
        help="Mapping file of RGB color in the SVG to brain region acronym. "
        "Defaults to downloading from the scalable brain atlas."
    )
    parser.add_argument(
        "--colormap-name",
        help="Name of the colormap to use to color the regions",
        default="hot")
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert the color map to flip low and high values.")
    parser.add_argument(
        "--colorbar",
        action="store_true",
        help="Draw a colorbar on the side of the SVG. (needs "
             "--segmentation-file argument)")
    parser.add_argument(
        "--segmentation-file",
        help="Compute the total # of voxels from this file (for the colorbar)")
    parser.add_argument(
        "--brain-volume",
        type=float,
        default=225.0,
        help="The brain volume in mm³. If the segmentation file is a "
             "hemisphere, remember to divide by 2."
    )
    return parser.parse_args()


def get_region_paths(svg_filename):
    """
    Find the XML elements that compose the region paths.

    :param svg_filename: Name of the .SVG file to read
    :return: a three-tuple of the XML tree, a list of path elements and the
    background rectangle.
    """
    tree = ET.parse(svg_filename)
    kids = tree.getroot().getchildren()
    grandkids = kids[0].getchildren()
    paths = [_ for _ in grandkids if _.tag == PATH_TAG]
    return tree, paths, grandkids[0]


def make_path_mappings(paths, brain_regions_file, rgb2acr_file=None):
    """
    Construct mappings of paths and IDs

    :param paths: the path elements parsed out of the SVG
    :param brain_regions_file: The filename of the AllBrainRegions.csv file
    :param rgb2acr_file: the filename of the json file giving the mapping
    between colors in the SVG and acronyms. If None, download from web.
    :return: a two-tuple of a list of two tuples of paths and IDs and a
    dictionary of path element indexed by ID.
    """
    structures = pandas.read_csv(brain_regions_file)

    with open(rgb2acr_file) \
            if rgb2acr_file is not None \
            else urlopen(RGB_2_ACR_URL) as fd:
        rgb2acr = json.load(fd)
    path_by_id = {}
    path_and_id = []
    for path in paths:
        color = path.attrib["fill"][1:]
        acronym = rgb2acr[color]
        str_id = structures.id[structures.acronym == acronym].values[0]
        path_by_id[str_id] = path
        path_and_id.append((path, str_id))
    return path_and_id, path_by_id


def make_intensity_map(data, segment_ids):
    """
    Create a map of densities per segment ID.
    :param data: a list of dataframes with count data in them
    :param segment_ids: a sequence of the segment IDs to map
    :return:
    """
    intensity_per_seg_id = {}
    for seg_id in segment_ids:
        for d in data:
            if np.sum(d.id == seg_id) > 0:
                count = d[d.id == seg_id]["count"].values[0]
                area = d[d.id == seg_id].area.values[0]
                break
            else:
                print("skipping segid=%d" % seg_id)
                count = 0
                area = 1
        intensity = count / area
        intensity_per_seg_id[seg_id] = intensity
    return intensity_per_seg_id

def calc_limits(data):
    """
    Calculate the minimum and maximum limits among all data

    :param data: a sequence of dataframes with count data in them
    :return: the minimum and maximum
    """
    imin, imax = [reduce(fn, [npfn(d["count"] / d.area) for d in data])
        for fn, npfn in ((min, np.min), (max, np.max))]
    return imin, imax

def recolor_path_elements(intensity_per_seg_id, path_and_id,
                          imin, imax,
                          colormap_name, invert=False):
    """
    Change the fill colors of the region path elements based on the
    densities in each region.

    :param intensity_per_seg_id: map of intensities for each segment ID
    :param path_and_id: two-tuple of path and segment ID
    :param imin: the minimum intensity among all data
    :param imax: the maximum intensity among all data
    :param colormap_name: The matplotlib colormap to use, e.g. "hot" or "jet"
    :param invert: If True, invert the color map so that low densities have
    stronger colors.
    """
    intensities = np.array(list(intensity_per_seg_id.values()))
    if invert:
        intensities = -intensities
    sm = matplotlib.cm.ScalarMappable(cmap=colormap_name)
    if invert:
        sm.set_clim(-imax, imin)
    else:
        sm.set_clim(imin, imax)
    colors = (sm.to_rgba(
        intensities) * 255).astype(int)
    color_per_seg_id = {}
    for seg_id, color in zip(intensity_per_seg_id.keys(), colors):
        color_per_seg_id[seg_id] = color
    for path, seg_id in path_and_id:
        if intensity_per_seg_id[seg_id] == 0:
            str_color = "#FFFFFF"
        else:
            color = color_per_seg_id[seg_id]
            str_color = "#%02x%02x%02x" % (color[0], color[1], color[2])
        path.attrib["fill"] = str_color
        path.attrib["stroke"] = "#AAAAAA"
        path.attrib["stroke-width"] = "1"
    return sm


def draw_colorbar(tree:ET.ElementTree,
                   colormap:matplotlib.cm.ScalarMappable,
                   invert:bool,
                   voxels_per_mm3:float,
                   title="counts/mm³"):
    """
    Expand the SVG to the right and put a colorbar there.
    :param tree: The XML element tree
    :param colormap: the color map to draw
    :param invert: Invert the color map intensities when labeling
    :param voxels_per_mm3: # of voxels per cubic millimeter
    """
    imin, imax = colormap.get_clim()
    imin_scale = imin * voxels_per_mm3
    imax_scale = imax * voxels_per_mm3
    if invert:
        imax_scale, imin_scale = -imin_scale, -imax_scale
        imin, imax = imax, imin
    svg = tree.getroot()
    g = svg.getchildren()[0]
    background_rect = [_ for _ in g.getchildren() if _.tag.endswith("rect")][0]
    old_width = int(svg.attrib["width"])
    new_width = old_width + 100
    svg.attrib["width"] = new_width
    height = int(svg.attrib["height"]) - 30
    top = 10
    left = old_width

    background_rect.attrib["width"] = str(new_width)
    svg.attrib["width"] = str(new_width)
    style_elem = ET.Element(STYLE_TAG)
    style_elem.text = """
    .title { font: bold 8pt sans-serif;}
    .annotation {font: bold 5pt sans-serif;}
    """
    svg.insert(0, style_elem)
    n_rects = 50
    rect_height = height / n_rects
    rect_y = np.linspace(20, 20+height, 50)
    colors = \
        (colormap.to_rgba(np.linspace(imax, imin, 50)) * 255).astype(int)
    for y, (red, green, blue, alpha) in zip(rect_y, colors):
        relem = ET.Element(RECT_TAG,
                           dict(x=str(old_width),
                                y=str(y),
                                width="50",
                                height=str(rect_height),
                                fill="#%02x%02x%02x" % (red, green, blue)))
        relem.attrib["stroke-width"] = "0"
        g.append(relem)
    title_elem = ET.Element(TEXT_TAG,
                            dict(x=str(old_width),
                                 y="15"))
    title_elem.attrib["class"] = "title"
    title_elem.text = title
    g.append(title_elem)
    max_elem = ET.Element(TEXT_TAG,
                          dict(x=str(old_width + 52),
                               y="25"))
    max_elem.attrib["class"] = "annotation"
    max_elem.text = str(int(imax_scale))
    g.append(max_elem)
    min_elem = ET.Element(TEXT_TAG,
                          dict(x=str(old_width + 52),
                               y=str(height + 20)))
    min_elem.attrib["class"] = "annotation"
    min_elem.text = str(int(imin_scale))
    g.append(min_elem)


def main():
    args = parse_args()
    tree, paths, rect = get_region_paths(args.svg_file)
    rect.attrib["fill"] = "#FFFFFF"
    data = [pandas.read_csv(_) for _ in args.count_file]
    path_and_id, path_by_id = make_path_mappings(
        paths, args.brain_regions_file, args.rgb2acr_file)
    intensity_per_seg_id = make_intensity_map(data, path_by_id.keys())
    imin, imax = calc_limits(data)
    sm = recolor_path_elements(intensity_per_seg_id, path_and_id, imin, imax,
                               args.colormap_name, args.invert)
    if args.colorbar:
        if args.segmentation_file is None:
            voxels_per_mm3 = 1000
            title = "Counts per KVoxel"
        else:
            n_voxels = np.sum(tifffile.imread(args.segmentation_file) != 0)
            voxels_per_mm3 = n_voxels / args.brain_volume
            title = "Counts per mm³"
        draw_colorbar(tree, sm, args.invert,
                      voxels_per_mm3=voxels_per_mm3,
                      title=title)
    tree.write(args.output)


if __name__ == "__main__":
    main()
