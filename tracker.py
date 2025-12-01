import math


class Tracker:
    def __init__(self, distance_threshold=85, max_disappeared=40):
        self.center_points = {}
        self.id_count = 0
        self.distance_threshold = distance_threshold
        self.max_disappeared = max_disappeared
        self.disappeared = {}

    def register(self, center):
        self.center_points[self.id_count] = center
        self.disappeared[self.id_count] = 0
        self.id_count += 1
        return self.id_count - 1

    def deregister(self, object_id):
        del self.center_points[object_id]
        del self.disappeared[object_id]

    def update(self, objects_rect):
        objects_bbs_ids = []

        input_centroids = []
        for rect in objects_rect:
            x, y, w, h = rect
            cx, cy = (x + x + w) // 2, (y + y + h) // 2
            input_centroids.append((cx, cy, x, y, w, h))

        if len(self.center_points) == 0:
            for i in range(len(input_centroids)):
                cx, cy, x, y, w, h = input_centroids[i]
                new_id = self.register((cx, cy))
                objects_bbs_ids.append([x, y, w, h, new_id])

        else:
            object_ids = list(self.center_points.keys())
            object_centroids = list(self.center_points.values())

            used_rows = set()
            used_cols = set()

            distances = []
            for i, object_id in enumerate(object_ids):
                for j, inp_cent in enumerate(input_centroids):
                    cx_old, cy_old = object_centroids[i]

                    cx_new, cy_new = inp_cent[0], inp_cent[1]

                    dist = math.hypot(cx_old - cx_new, cy_old - cy_new)
                    distances.append((dist, i, j))

            distances.sort(key=lambda x: x[0])

            for dist, row, col in distances:
                if row in used_rows or col in used_cols:
                    continue

                if dist > self.distance_threshold:
                    continue

                object_id = object_ids[row]
                cx_new, cy_new, x, y, w, h = input_centroids[col]

                self.center_points[object_id] = (cx_new, cy_new)
                self.disappeared[object_id] = 0
                objects_bbs_ids.append([x, y, w, h, object_id])

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(len(object_ids))) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            unused_cols = set(range(len(input_centroids))) - used_cols
            for col in unused_cols:
                cx, cy, x, y, w, h = input_centroids[col]
                new_id = self.register((cx, cy))
                objects_bbs_ids.append([x, y, w, h, new_id])

        return objects_bbs_ids