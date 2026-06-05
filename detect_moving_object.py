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

    ego_velocity_threshold = 0.6
    threshold_distance_to_sensor = 2.0

    dangerous_clusters = []

    if ego_velocity < ego_velocity_threshold:
        return dangerous_clusters

    for current_cluster in clusters_current:

        cluster_id = current_cluster["id"]

        if cluster_id is None:
            continue

        distance_to_sensor = (current_cluster["center"]["distance_mean_origin"])

        if distance_to_sensor > threshold_distance_to_sensor:
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

    return dangerous_clusters
