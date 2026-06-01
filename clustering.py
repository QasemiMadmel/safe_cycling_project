# cluster_per_scan

import numpy as np


def create_empty_segment(num_scan):
    return {
        "num_scan": num_scan,
        "id":None,
        "x": [],
        "y": [],
        "center": {
            "x": None,
            "y": None
        },
        "length": 0
    }


def cluster_segments(x, y, num_scan):

    upper_threshold = 0.5
    lower_threshold = 0.005

    segments = []
    segment_started = False

    current_segment = create_empty_segment(num_scan)

    for i in range(len(x) - 1):

        if np.isnan(x[i]) or np.isnan(x[i + 1]):
            continue

        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]

        distance = np.sqrt(dx**2 + dy**2)

        if lower_threshold < distance < upper_threshold:

            segment_started = True

            current_segment["x"].append(x[i])
            current_segment["y"].append(y[i])

        else:

            if segment_started:

                current_segment["center"]["x"] = np.mean(current_segment["x"])
                current_segment["center"]["y"] = np.mean(current_segment["y"])
                current_segment["length"] = len(current_segment["x"])

                segments.append(current_segment)

                current_segment = create_empty_segment(num_scan)
                segment_started = False

    # in case the last point is within a segment
    if segment_started:

        current_segment["center"]["x"] = np.mean(current_segment["x"])
        current_segment["center"]["y"] = np.mean(current_segment["y"])
        current_segment["length"] = len(current_segment["x"])

        segments.append(current_segment)

    return segments


def merge_segments_into_clusters(segments):

    threshold_x = 0.5
    merge_threshold = 0.7
    min_cluster_size = 3
    merged_clusters = []
    used = [False] * len(segments)

    for i in range(len(segments)):

        if used[i]:
            continue

        current_segment = segments[i]
        used[i] = True

        for k in range(i + 1, len(segments)):
            if used[k]:
                continue

            delta_x = np.abs(current_segment["center"]["x"] - segments[k]["center"]["x"])
            delta_y = np.abs(current_segment["center"]["y"] - segments[k]["center"]["y"])
            mean_distance = np.sqrt(delta_x**2 + delta_y**2)

            if delta_x < threshold_x or mean_distance < merge_threshold:
                current_segment["x"].extend(segments[k]["x"])
                current_segment["y"].extend(segments[k]["y"])
                current_segment["center"]["x"] = np.mean(current_segment["x"])
                current_segment["center"]["y"] = np.mean(current_segment["y"])
                current_segment["length"] = len(current_segment["x"])
                used[k] = True

        if current_segment["length"] >= min_cluster_size:
            merged_clusters.append(current_segment)

    return merged_clusters
