import argparse
import json
import neuroglancer
import numpy as np
import os
import sys
import tifffile
import webbrowser
import time

viewer = None

def say(msg, category):
    with viewer.config_state.txn() as txn:
        txn.status_messages[category] = msg

def action_handler(viewer, s, min_distance):
    point = s.mouse_voxel_coordinates
    print( dir(s), type(s))
    with viewer.txn() as txn:
        points = [_.point.tolist()
                  for _ in txn.layers["annotation"].annotations]
        if any([np.sqrt(sum([(a - b) ** 2 for a, b in zip(p, point)]))
                < min_distance
                for p in points]):
            say("Point too close to some other point!", "annotation")
            return
        points.append(point.tolist())
        txn.layers["annotation"] = \
            neuroglancer.viewer_state.PointAnnotationLayer(points=points)
        say("Added point at %.2f, %.2f, %.2f" % (point[0], point[1], point[2]),
            "annotation")

def delete_handler(s, min_distance):
    point = s.mouse_voxel_coordinates
    with viewer.txn() as txn:
        points = [_.point.tolist()
                  for _ in txn.layers["annotation"].annotations]
        if len(points) == 0:
            say("No points to delete", "delete")
            return
        distances = np.sqrt([sum([(a - b) ** 2 for a, b in zip(p, point)])
                             for p in points])
        idx = np.argmin(distances)
        if distances[idx] > min_distance:
            say("Not close enough to any point to delete", "delete")
        else:
            say("Deleting %.2f, %.2f, %.2f" % (points[idx][0],
                                               points[idx][1],
                                               points[idx][2]), "delete")
            points.pop(idx)
            txn.layers["annotation"] = \
                neuroglancer.viewer_state.PointAnnotationLayer(points=points)
            
def save(viewer, output):
    points = [_.point.tolist() for
              _ in viewer.state.layers["annotation"].annotations]
    if os.path.exists(output):
        if os.path.exists(output+".old"):
            os.remove(output+".old")
        os.rename(output, output+".old")
    json.dump(points, open(output, "w"))

def main():
    global viewer
    parser = argparse.ArgumentParser(description="NeUroGlancer Ground Truth")
    parser.add_argument("--port", type=int, help="HTTP port for server", default=0)
    parser.add_argument("--image", help="Path to image file", required=True)
    parser.add_argument("--output", help="Path to list of point annotations", required=True)
    parser.add_argument("--min-distance",
                        help="Minimum distance between two annotations",
                        type=int, default=10)
    args = parser.parse_args()

    if os.path.exists(args.output):
        points = np.array(json.load(open(args.output)), np.float32)
    else:
        points = []

    neuroglancer.set_server_bind_address(bind_port=args.port)

    img = tifffile.imread(args.image)

    viewer = neuroglancer.Viewer()
    with viewer.txn() as s:
        s.voxel_size = [1000, 1000, 1000]
        s.layers["image"] = neuroglancer.ImageLayer(
            source=neuroglancer.LocalVolume(img, voxel_size=s.voxel_size))
        s.layers["annotation"] = \
            neuroglancer.PointAnnotationLayer(points=points)
    save_fn = lambda s: save(viewer, args.output)
    annotate_fn = lambda s:action_handler(viewer, s, args.min_distance)
    delete_fn = lambda s:delete_handler(s, args.min_distance)
    viewer.actions.add("save", save_fn)
    viewer.actions.add("annotatepts", annotate_fn)
    viewer.actions.add("deletepts", delete_fn)
    with viewer.config_state.txn() as s:
        s.input_event_bindings.viewer["keyt"] = "annotatepts"
        s.input_event_bindings.viewer["keyu"] = "save"
        s.input_event_bindings.viewer["keyv"] = "deletepts"
    print(viewer)
    webbrowser.open_new(viewer.get_viewer_url())
    print("Hit control-c to exit")
    while True:
        time.sleep(10)

if __name__=="__main__":
    main()
