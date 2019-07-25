"""ngutils - utilities for manipulating a neuroglancer viewer


"""
from copy import deepcopy
import numpy as np
import neuroglancer

"""A shader that displays an image as gray in Neuroglancer"""
gray_shader = """
void main() {
   emitGrayscale(%f * toNormalized(getDataValue()));
}
"""

"""A shader that displays an image in red in Neuroglancer"""
red_shader = """
void main() {
   emitRGB(vec3(%f * toNormalized(getDataValue()), 0, 0));
}
"""

"""A shader that displays an image in green in Neuroglancer"""
green_shader = """
void main() {
   emitRGB(vec3(0, %f * toNormalized(getDataValue()), 0));
}
"""

"""A shader that displays an image in blue in Neuroglancer"""
blue_shader = """
void main() {
   emitRGB(vec3(0, 0, %f * toNormalized(getDataValue())));
}
"""

"""A shader that displays an image using the classic Jet colormap"""
jet_shader = """

void main() {
  float x = clamp(toNormalized(getDataValue()) * %f, 0.0, 1.0);
  vec3 result;
  result.r = x < 0.89 ? ((x - 0.35) / 0.31) : (1.0 - (x - 0.89) / 0.11 * 0.5);
  result.g = x < 0.64 ? ((x - 0.125) * 4.0) : (1.0 - (x - 0.64) / 0.27);
  result.b = x < 0.34 ? (0.5 + x * 0.5 / 0.11) : (1.0 - (x - 0.34) / 0.31);
   emitRGB(result);
}
"""

"""A shader for the cubehelix color scheme
"""
#
# Code borrowed in part from
# https://www.mrao.cam.ac.uk/~dag/CUBEHELIX/CubeHelix.m
# published under the Unlicense: (http://unlicense.org/)
#
cubehelix_shader = """
void main() {
    float x = clamp(toNormalized(getDataValue()) * %f, 0.0, 1.0);
    float angle = 2.0 * 3.1415926 * (4.0 / 3.0 + x);
    float amp = x * (1.0 - x) / 2.0;
    vec3 result;
    float cosangle = cos(angle);
    float sinangle = sin(angle);
    result.r = -0.14861 * cosangle + 1.78277 * sinangle;
    result.g = -0.29227 * cosangle + -0.90649 * sinangle;
    result.b = 1.97294 * cosangle;
    result = clamp(x + amp * result, 0.0, 1.0);
    emitRGB(result);
}
"""
#
# Monkey-patch Neuroglancer to control the color of the annotation dots
#
if not hasattr(neuroglancer.PointAnnotationLayer, "annotation_color"):
    from neuroglancer.viewer_state import  wrapped_property, optional, text_type
    neuroglancer.PointAnnotationLayer.annotation_color = \
        wrapped_property('annotationColor', optional(text_type))

default_voxel_size = (1000, 1000, 1000)


def soft_max_brightness(img, percentile=99.9):
    """
    Compute a soft maximum brightness for an image based on almost all the
    voxels

    :param img: The image to compute
    :param percentile: the percentile to use - pick the brightness at this
    percentile
    :return: the soft max brightness
    """
    result = np.percentile(img, percentile)
    if result == 0:
        result = max(np.finfo(np.float32).eps, np.max(img))
    return result


def layer(txn, name, img, shader, multiplier, offx=0, offy=0, offz=0,
          voxel_size=default_voxel_size):
    """Add an image layer to Neuroglancer

    :param txn: The transaction context of the viewer

    :param name: The name of the layer as displayed in Neuroglancer

    :param img: The image to display

    :param shader: the shader to use when displaying, e.g. gray_shader

    :param multiplier: the multiplier to apply to the normalized data value.
    This can be used to brighten or dim the image.
    """
    if isinstance(img, str):
        frac = multiplier
        source = img
    else:
        frac = multiplier / soft_max_brightness(img)
        if img.dtype.kind in ("i", "u"):
            frac = frac * np.iinfo(img.dtype).max
        source = neuroglancer.LocalVolume(img,
                                          voxel_offset=(offx, offy, offz),
                                          voxel_size=voxel_size)
    txn.layers[name] = neuroglancer.ImageLayer(
        source=source,
        shader = shader % frac
    )


def seglayer(txn, name, seg, offx=0, offy=0, offz=0,
             voxel_size=default_voxel_size):
    """Add a segmentation layer

    :param txn: the neuroglancer transaction

    :param name: the display name of the segmentation

    :param seg: the segmentation to display
    """
    txn.layers[name] = neuroglancer.SegmentationLayer(
        source=neuroglancer.LocalVolume(
            seg.astype(np.uint16),
            voxel_offset=(offx, offy, offz),
            voxel_size=voxel_size))


def pointlayer(txn, name, x, y, z, color):
    """Add a point layer

    :param txn: the neuroglancer viewer transaction context

    :param name: the displayable name of the point layer

    :param x: the x coordinate per point

    :param y: the y coordinate per point

    :param z: the z coordinate per point

    :param color: the color of the points in the layer, e.g. "red", "yellow"
    """
    txn.layers[name] = neuroglancer.PointAnnotationLayer(
        points=np.column_stack((x, y, z)),
        annotation_color=color
    )


def bboxlayer(txn, name, x0, x1, y0, y1, z0, z1):
    """Add a bounding box layer

    :param txn: the neuroglancer viewer transaction context
    :param name: the name of the layer
    :param x0: the leftmost edge of the box
    :param x1: the rightmost edge of the box
    :param y0: the topmost edge of the box
    :param y1: the bottommoste edge of the box
    :param z0: the most shallow depth of the box
    :param z1: the deepest edge of the box
    """
    box = neuroglancer.AxisAlignedBoundingBoxAnnotation()
    box.point_a = [x0, y0, z0]
    box.point_b = [x1, y1, z1]
    box.id = name
    txn.layers[name] = neuroglancer.AnnotationLayer(annotations=[box])


def has_layer(txn, name):
    """Return true if the viewer state has a layer with the given name

    :param txn: A viewer state transaction, e.g. viewer.txn()
    :param name: the layer name to search for
    """
    for layer in txn.layers:
        if layer.name == name:
            return True
    return False

def post_message_immediately(viewer, topic, message):
    """Post a message to a viewer w/o waiting for the event loop

    :param viewer: the neuroglancer viewer
    :param topic: the status message topic
    :param message: the message to display
    """
    cs, generation = \
        viewer.config_state.state_and_generation
    cs = deepcopy(cs)

    cs.status_messages[topic] = message
    viewer.config_state.set_state(
        cs, existing_generation=generation)
    ioloop = neuroglancer.server.global_server.ioloop
    cb = ioloop._callbacks.pop()
    try:
        ioloop._run_callback(cb)
    except:
        ioloop._callbacks.push(cb)
