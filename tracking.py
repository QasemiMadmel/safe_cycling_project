# tracking.py

import numpy as np


# to determine wethear the cluster is moving toward the sensor or away from it   
def determine_cluster_direction(cluster, dy):
        if (dy < 0):
                cluster["approaching"] = True
        else: 
                cluster["approaching"] = False
 
   
# how fast is the cluster moving
def determine_longitudinal_speed(distance_dy, dt):
	if distance_dy is None or dt <= 0: 
            return 0
	else:
            cluster_velocity = distance_dy / dt
            return cluster_velocity  


# to set default id's for clusters of the first four scans 
def set_default_id(scan, next_id):
        
	for cluster in scan: 
                cluster["id"] = next_id
                cluster["approaching"] = False
                cluster["speed"] = 0
                next_id += 1
                
	return next_id

# track based on distances in between clusters in subsequent scans         
def track_clusters(
        three_scans_ago,
        two_scans_ago,
        previous_scan,
        current_scan,
        next_id,
        dt):

	# threshold for distance of same clusters in two different scans 
    distance_threshold_scan_before = 0.8
    distance_threshold_between_more_scanes = 1

	# go over the curent scan clusters
    for current_cluster in current_scan:

        # flag to exit the tracking process once a match has been found
        cluster_matched = False

        #
        # Scan -1
        #
        closest_distance = np.inf
        closest_dy = None
        closest_id = None

		# go over all clusters in the previous scan (scan -1)
        for old_cluster in previous_scan:

			# compuet the distances between the center of clusters 
            dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
            dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]
            distance = np.sqrt(dx**2 + dy**2)

            # out of all distances, store the lowest with the corredsponding cluster id   
            if distance < closest_distance:
                closest_distance = distance
                closest_dy = dy
                closest_id = old_cluster["id"]
		
        # is the cluster with the lowest distance within the threshold range? if yes, the cluster is tracked
        if closest_distance < distance_threshold_scan_before:

            current_cluster["id"] = closest_id
            determine_cluster_direction(current_cluster, closest_dy)
            current_cluster["speed"] = determine_longitudinal_speed(abs(closest_dy), dt)
            cluster_matched = True
            
		# otherwise look for a match in two or three scans earlier and apply the same logic
        
		#
        # Scan -2
        #
        if not cluster_matched:

            closest_distance = np.inf
            closest_dy = None
            closest_id = None

            for old_cluster in two_scans_ago:

                dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
                dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]

                distance = np.sqrt(dx**2 + dy**2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_dy = dy
                    closest_id = old_cluster["id"]

            if closest_distance < distance_threshold_between_more_scanes:

                current_cluster["id"] = closest_id
                determine_cluster_direction(current_cluster, closest_dy)
                current_cluster["speed"] = determine_longitudinal_speed(abs(closest_dy), dt*2)
                cluster_matched = True

        #
        # Scan -3
        #
        if not cluster_matched:

            closest_distance = np.inf
            closest_dy = None
            closest_id = None

            for old_cluster in three_scans_ago:

                dx = current_cluster["center"]["x"] - old_cluster["center"]["x"]
                dy = current_cluster["center"]["y"] - old_cluster["center"]["y"]

                distance = np.sqrt(dx**2 + dy**2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_dy = dy
                    closest_id = old_cluster["id"]

            if closest_distance < distance_threshold_between_more_scanes:

                current_cluster["id"] = closest_id
                determine_cluster_direction(current_cluster, closest_dy)
                current_cluster["speed"] = determine_longitudinal_speed(abs(closest_dy), dt*3)
                cluster_matched = True


        #
        # if no matches are found the give the cluster a new ID
        #
        if not cluster_matched:

            current_cluster["id"] = next_id
            current_cluster["approaching"] = False 
            current_cluster["speed"] = 0
            next_id += 1
            
    return current_scan, next_id




