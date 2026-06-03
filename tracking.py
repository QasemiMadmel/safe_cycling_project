# tracking.py

import numpy as np

def track_clusters(
        three_scans_ago,
        two_scans_ago,
        previous_scan,
        current_scan,
        next_id):

    threshold = 0.8

    for current_cluster in current_scan:

        cluster_matched = False

        #
        # Scan -1
        #
        closest_distance = np.inf
        closest_id = None

        for old_cluster in previous_scan:

            dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
            dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]

            distance = np.sqrt(dx**2 + dy**2)

            if distance < closest_distance:
                closest_distance = distance
                closest_id = old_cluster["id"]

        if closest_distance < threshold:

            current_cluster["id"] = closest_id
            cluster_matched = True

        #
        # Scan -2
        #
        if not cluster_matched:

            closest_distance = np.inf
            closest_id = None

            for old_cluster in two_scans_ago:

                dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
                dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]

                distance = np.sqrt(dx**2 + dy**2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_id = old_cluster["id"]

            if closest_distance < threshold:

                current_cluster["id"] = closest_id
                cluster_matched = True

        #
        # Scan -3
        #
        if not cluster_matched:

            closest_distance = np.inf
            closest_id = None

            for old_cluster in three_scans_ago:

                dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
                dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]

                distance = np.sqrt(dx**2 + dy**2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_id = old_cluster["id"]

            if closest_distance < threshold:

                current_cluster["id"] = closest_id
                cluster_matched = True

        #
        # new ID
        #
        if not cluster_matched:

            current_cluster["id"] = next_id
            next_id += 1

    return current_scan, next_id


def set_default_id(scan, next_id):
	
	for cluster in scan: 
		cluster["id"] = next_id
		next_id += 1
	    
	return next_id
