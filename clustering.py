# cluster_per_scan

import numpy as np

# create a directory to store specific data for each segment/cluster
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

    # thresholds allowed between two neighbouring points for ´segmentation process
    upper_threshold = 0.5
    lower_threshold = 0.005

    segments = []
    segment_started = False

    # create empty directory for storing data
    current_segment = create_empty_segment(num_scan)

    # go over all x and y values
    for i in range(len(x) - 1):

        if np.isnan(x[i]) or np.isnan(x[i + 1]):
            continue

        # compute the distance of two neighbouring points
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]

        distance = np.sqrt(dx**2 + dy**2)

        # check wether it is in range 
        if lower_threshold < distance < upper_threshold:
            # if yes set a flag and store the values
            segment_started = True
            current_segment["x"].append(x[i])
            current_segment["y"].append(y[i])
        else:
             # if the distance between neighbouring points is beyond thresholds, 
             # compute mean values for the segment and store the properties
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

    # one scan can have multiple segments that actually represent one single object
    # if the distance between the center of two (or more) segments in one scan is below a certain threshold
    # they are merged into one cluster
    threshold_x = 0.5
    merge_threshold = 0.8
    min_cluster_size = 3
    merged_clusters = []
    used = [False] * len(segments)

    # go over all segments
    for i in range(len(segments)):

        if used[i]:
            continue

        # take one segement and mark it
        current_segment = segments[i]
        used[i] = True

        # now go over all other segments in scan 
        for k in range(i + 1, len(segments)):
            if used[k]:
                continue

            # compute the distance of the mean valeus
            delta_x = np.abs(current_segment["center"]["x"] - segments[k]["center"]["x"])
            delta_y = np.abs(current_segment["center"]["y"] - segments[k]["center"]["y"])
            mean_distance = np.sqrt(delta_x**2 + delta_y**2)

            # check if they are close enough to be merged 
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
