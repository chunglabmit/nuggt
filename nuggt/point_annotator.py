import numpy as np
import neuroglancer
from nuggt.utils.ngutils import *

class PointAnnotator:

    def __init__(self, viewer, color="yellow"):
        self.points = np.zeros((0, 3))
        self.deleting_points = np.zeros((0, 3))
        self.viewer = viewer
        self.color = color
        self.min_distance = 5
        self.box_coords = None
        self.viewer.actions.add("annotatepts", self.on_annotate_point)
        self.viewer.actions.add("deletepts", self.on_delete_point)
        self.viewer.actions.add("start-selection",
                                self.start_selection_handler)
        self.viewer.actions.add("extend-selection",
                                self.extend_selection_handler)
        self.viewer.actions.add("delete-selected",
                                self.delete_selected_handler)
        with self.viewer.config_state.txn() as s:
            s.input_event_bindings.viewer["shift+keya"] = "annotatepts"
            s.input_event_bindings.viewer["shift+keyd"] = "deletepts"
            s.input_event_bindings.viewer["bracketleft"] = "start-selection"
            s.input_event_bindings.viewer["bracketright"] = "extend-selection"
            s.input_event_bindings.viewer["shift+keyx"] = "delete-selected"

    def set_points(self, points):
        self.points = points
        self.display_points()

    def display_points(self):
        with self.viewer.txn() as txn:
            pointlayer(txn, "points", self.points[:, 0], self.points[:, 1],
                       self.points[:, 2], self.color)
            if self.deleting_points is not None:
                pointlayer(txn, "delete-points",
                           self.deleting_points[:, 0],
                           self.deleting_points[:, 1],
                           self.deleting_points[:, 2],
                           "red")
            if self.box_coords is not None:
                box = neuroglancer.AxisAlignedBoundingBoxAnnotation()
                box.point_a = self.box_coords[0]
                box.point_b = self.box_coords[1]
                box.id = "selection"
                txn.layers["selection"] = neuroglancer.AnnotationLayer(
                    annotations=[box])
            elif "selection" in txn.layers:
                del txn.layers["selection"]

    def say(self, msg, category):
        with self.viewer.config_state.txn() as txn:
            txn.status_messages[category] = msg

    def on_annotate_point(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        neighbors = self.find_nearby_points(point)
        if len(neighbors) > 0:
            self.say("Point too close to some other point!", "annotation")
            return
        self.points = np.vstack((self.points, point))
        self.display_points()
        self.say("Added point at %.2f, %.2f, %.2f" %
                 (point[0], point[1], point[2]),
            "annotation")

    def find_nearby_points(self, point, return_index=False):
        if len(self.points) == 0:
            if return_index:
                return np.zeros((0, 3), np.float32), np.zeros(0, int)
            else:
                return np.zeros((0, 3), np.float32)

        diff = self.points - point[np.newaxis, :]
        distances = np.sqrt(np.sum(np.square(diff), 1))
        indexes = np.where(distances < self.min_distance)[0]
        if len(indexes) == 0:
            if return_index:
                return np.zeros((0, 3), np.float32), np.zeros(0, int)
            else:
                return np.zeros((0, 3), np.float32)
        result = self.points[indexes]
        order = np.argsort(distances[indexes])
        if return_index:
            return result[order], indexes[order]
        else:
            return result[order]

    def on_delete_point(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        neighbors, indexes = self.find_nearby_points(point, return_index=True)
        if len(neighbors) == 0:
            self.say("No nearby point", "delete")
            return
        to_delete = self.points[indexes[0]]
        self.points = np.delete(self.points, indexes[0], 0)
        self.display_points()
        self.say("Deleting %.2f, %.2f, %.2f" %
            (to_delete[0], to_delete[1], to_delete[2]), "delete")

    def partition_points(self):
        """Partition points inside/outside bounding box"""
        for idx in range(3):
            if self.box_coords[0][idx] == self.box_coords[1][idx]:
                self.box_coords[1][idx] += 1
        (x0, x1), (y0, y1), (z0, z1) = [
            [fn(self.box_coords[0][idx], self.box_coords[1][idx])
             for fn in (min, max)] for idx in range(3)]
        all_points = self.all_points
        mask = (all_points[:, 0] >= x0) & (all_points[:, 0] < x1) & \
               (all_points[:, 1] >= y0) & (all_points[:, 1] < y1) & \
               (all_points[:, 2] >= z0) & (all_points[:, 2] < z1)
        self.points, self.deleting_points = all_points[~mask], all_points[mask]
        self.display_points()

    def start_selection_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        if self.box_coords is None:
            self.box_coords = [point, point + 20]
        else:
            self.box_coords[0] = point
        self.partition_points()

    def extend_selection_handler(self, s):
        point = np.array(s.mouse_voxel_coordinates)
        if self.box_coords is None:
            self.box_coords = [point-20, point]
        else:
            self.box_coords[1] = point
        self.partition_points()

    def delete_selected_handler(self, s):
        if self.box_coords is not None:
            self.box_coords = None
            self.deleting_points = None
            with self.viewer.txn() as txn:
                del txn.layers["selection"]
                del txn.layers["delete-points"]

    @property
    def all_points(self):
        """Both the regular points and those in the delete bucket"""
        if self.deleting_points is not None:
            return np.vstack((self.points, self.deleting_points))
        else:
            return self.points
