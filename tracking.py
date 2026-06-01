import numpy as np

def track_clusters(scan_previous_with_clusters, scan_current_with_clusters):

    threshold = 0.8
    match_found = False
    
    for current_cluster in scan_current_with_clusters:
        closest_mean_distance = np.inf
        closest_cluster_id = None

        for previous_scan_cluster in scan_previous_with_clusters:

            delta_x = (current_cluster["center"]["x"] - previous_scan_cluster["center"]["x"])
            delta_y = (current_cluster["center"]["y"] - previous_scan_cluster["center"]["y"])

            distance = np.sqrt(delta_x**2 + delta_y**2)

            if distance < closest_mean_distance:

                closest_mean_distance = distance
                closest_cluster_id = previous_scan_cluster["id"]

        if closest_mean_distance < threshold and closest_cluster_id is not None:
            current_cluster["id"] = closest_cluster_id
            match_found = True            

    return scan_current_with_clusters, match_found
