import numpy as np


def find_cluster_by_id(clusters, cluster_id):

    for cluster in clusters:

        if cluster["id"] == cluster_id:
            return cluster

    return None


def detect_danger(ego_velocity,
                scan_number,
                clusters_current,
                previous_scan,
                clusters_two_scans_ago,
                clusters_three_scans_ago):

    ego_velocity_threshold_side = 3 # about 11 km/h
    ego_velocity_threshold_back = 5 # about 18 km/h
    threshold_distance_to_sensor_side = 2.0
    threshold_distance_to_sensor_back = 3.0

    dangerous_clusters = []

    for current_cluster in clusters_current:

        x_mean = current_cluster["center"]["x"]
        y_mean = current_cluster["center"]["y"]

        is_side = (
            0.2 < x_mean < 3 and
            0.2 < y_mean < 2
        )
        
        is_back = (
            -0.5 < x_mean < 1.5 and
            0.2 < y_mean < 4
        )
        
        cluster_id = current_cluster["id"]

        if cluster_id is None:
            continue
        
        if is_side:
            
            if ego_velocity > ego_velocity_threshold_side:
            
                distance_to_sensor = (current_cluster["center"]["distance_mean_origin"])

                if distance_to_sensor > threshold_distance_to_sensor_side:
                    continue

                direction = []

                scans_to_check = [previous_scan, clusters_two_scans_ago, clusters_three_scans_ago]
                current_y = current_cluster["center"]["y"]

                for old_scan in scans_to_check:

                    old_cluster = find_cluster_by_id(old_scan, cluster_id)
                    if old_cluster is None:
                        continue
                    old_y = old_cluster["center"]["y"]
                    delta_y = current_y - old_y

                    if delta_y < 0:
                        direction.append(True)
                    else:
                        direction.append(False)

                if len(direction) == 0:
                    continue

                moves_toward_sensor = (sum(direction) > len(direction) / 4)
                current_cluster["moves_toward_sensor"] = moves_toward_sensor

                if moves_toward_sensor:

                    danger = {
                        "scan_number": scan_number,
                        "cluster_id": cluster_id,
                        "distance_to_sensor": distance_to_sensor,
                        "ego_velocity": ego_velocity
                    }

                    dangerous_clusters.append(danger)
        elif is_back: 
            
            if ego_velocity > ego_velocity_threshold_back:
                
                distance_to_sensor = (current_cluster["center"]["distance_mean_origin"])

                if distance_to_sensor < threshold_distance_to_sensor_back:
                    danger = {
                    "scan_number": scan_number,
                    "cluster_id": cluster_id,
                    "distance_to_sensor": distance_to_sensor,
                    "ego_velocity": ego_velocity
                    }
                    dangerous_clusters.append(danger)
                
            

    return dangerous_clusters
