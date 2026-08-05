# clustering.py

import numpy as np


# creates default segment
def create_empty_segment(num_scan):
    return {
        "num_scan": num_scan,
        "id": None,
        "x": [],
        "y": [],
        "center": {
            "x": None,
            "y": None,
            "distance_mean_origin": None
        },
        "length": 0
    }


# adds mean value and the distance to a segment or cluster 
def update_segment_properties(cluster):

    if len(cluster["x"]) == 0:
        return

    mean_x = np.mean(cluster["x"])
    mean_y = np.mean(cluster["y"])

    cluster["center"]["x"] = mean_x
    cluster["center"]["y"] = mean_y
    cluster["center"]["distance_mean_origin"] = np.sqrt(mean_x**2 + mean_y**2)
    cluster["length"] = len(cluster["x"])
    cluster["speed"] = 0


# search for segments in a single scan based on distances in between points 
def find_segments(x, y, num_scan):

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
                update_segment_properties(current_segment)
                segments.append(current_segment)
                current_segment = create_empty_segment(num_scan)
                segment_started = False

    if segment_started:

        update_segment_properties(current_segment)
        segments.append(current_segment)

    return segments


# if segments are close to each other, then they probably belong to the same cluster: merging function
def merge_segments_into_clusters(segments):

    threshold_x = 0.5
    merge_threshold = 0.8
    min_cluster_size = 10

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

            dx = abs(current_segment["center"]["x"] - segments[k]["center"]["x"])
            dy = abs(current_segment["center"]["y"] - segments[k]["center"]["y"])

            distance_between_segments = np.sqrt(dx**2 + dy**2)

            if (dx < threshold_x or distance_between_segments < merge_threshold):

                current_segment["x"].extend(segments[k]["x"])
                current_segment["y"].extend(segments[k]["y"])
                update_segment_properties(current_segment)

                used[k] = True

        if current_segment["length"] >= min_cluster_size:
            merged_clusters.append(current_segment)

    return merged_clusters
