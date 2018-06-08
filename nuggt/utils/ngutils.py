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

#
# Monkey-patch Neuroglancer to control the color of the annotation dots
#
if not hasattr(neuroglancer.PointAnnotationLayer, "annotation_color"):
    from neuroglancer.viewer_state import  wrapped_property, optional, text_type
    neuroglancer.PointAnnotationLayer.annotation_color = \
        wrapped_property('annotationColor', optional(text_type))

voxel_size = (1000, 1000, 1000)


def layer(txn, name, img, shader, multiplier, offx=0, offy=0, offz=0):
    """Add an image layer to Neuroglancer

    :param txn: The transaction context of the viewer

    :param name: The name of the layer as displayed in Neuroglancer

    :param img: The image to display

    :param shader: the shader to use when displaying, e.g. gray_shader

    :param multiplier: the multiplier to apply to the normalized data value.
    This can be used to brighten or dim the image.
    """
    txn.layers[name] = neuroglancer.ImageLayer(
        source = neuroglancer.LocalVolume(img,
                                          voxel_offset=(offx, offy, offz),
                                          voxel_size=voxel_size),
        shader = shader % (multiplier / np.percentile(img, 99.9))
    )


def seglayer(txn, name, seg, offx=0, offy=0, offz=0):
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
