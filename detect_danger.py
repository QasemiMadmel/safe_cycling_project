# detect_danger.py 

import numpy as np

def find_cluster_by_id(clusters, cluster_id):

    for cluster in clusters:

        if cluster["id"] == cluster_id:
            return cluster

    return None

def moves_in_sensor_direction(clusters_in_previous_scan,
                            clusters_two_scans_ago,
                            clusters_three_scans_ago, 
                            current_id): 
    # gather all scans in one array
    scans_to_check = [clusters_in_previous_scan, clusters_two_scans_ago, clusters_three_scans_ago]
    
    # for storing the results 
    directions = [] 
    
    # for each cluster in current scan, go over all past clusters with the same id
    for scan in scans_to_check:
        corresponding_previous_cluster = find_cluster_by_id(scan, current_id)
        
        # gather the information about the moving directoin
        if corresponding_previous_cluster is None: 
            continue
        else: 
            directions.append(corresponding_previous_cluster["approaching"]) 
        
    
    if len(directions) == 0:
        return False
    
    # majority determines weather the cluster is moving toward to sensor or away form sensor
    moves_toward_sensor = (sum(directions) > len(directions)/4)
        
    return moves_toward_sensor
                    
def distiguish_scenario_and_detect_danger(ego_velocity, 
                scan_number,
                clusters_in_current_scan,
                clusters_in_previous_scan,
                clusters_two_scans_ago,
                clusters_three_scans_ago):

    # thresholds for velocities and distances  
    ego_velocity_threshold = 0.6 # ~2[km/h]
    velocity_threshold = 0.3 # ~1[km/h]
    
    longitudinal_distance_to_sensor_threshold = 6.0
    distance_to_distinguish_scenarios = 0.5
    lateral_distance_to_sensor_threshold = 1.5
    absolute_minimal_distance_for_tailgating = 5.0

    # array for storing the results 
    dangerous_clusters = []
    
    # go over all clusters in current scan
    for current_cluster in clusters_in_current_scan:

        # save the id and velocity of the investigated cluster
        cluster_id = current_cluster["id"]
        cluster_speed = current_cluster["speed"]
        
        # is the bicycle moving? 
        if ego_velocity > ego_velocity_threshold:
            
            # distinguish the scenario based on the position of cluster
            x = np.asarray(current_cluster["x"])
            y = np.asarray(current_cluster["y"])     
                       
            minimal_distance_dx = np.min(x)
            minimal_distance_y = np.min(y)
            index_of_minimal_y = np.argmin(y)
            corresponding_dx_to_minimal_ditance_from_y = x[index_of_minimal_y]
            
            # cluster in warning area?
            if minimal_distance_y < longitudinal_distance_to_sensor_threshold: 
                
                # which scenario -> overtaking or tailgating? 
                if (minimal_distance_dx < distance_to_distinguish_scenarios 
                    or corresponding_dx_to_minimal_ditance_from_y < distance_to_distinguish_scenarios): 

                    # tailgating scenario and the car s already too close to sensor
                    if minimal_distance_y < absolute_minimal_distance_for_tailgating: 
                    
                        # store in danger 
                        danger = {"scan_number": scan_number,
                                "cluster_id": cluster_id,
                                "distance_sensor_longitudinal": minimal_distance_y,
                                "distance_sensor_lateral_dx": minimal_distance_dx,
                                "ego_velocity": ego_velocity,
                                "cluster_speed": cluster_speed,
                                "scenario": "tailgating"}
                        dangerous_clusters.append(danger)
                        
                # if the car is trying to overtake and has insufficeint lateral distance
                elif (minimal_distance_dx < lateral_distance_to_sensor_threshold
                    or corresponding_dx_to_minimal_ditance_from_y < lateral_distance_to_sensor_threshold): 
                        # overtaking scenario 
                        # (dangerous when car is moving toward cyclist)  
                     
                        car_is_moving_toward_sensor = moves_in_sensor_direction(clusters_in_previous_scan, clusters_two_scans_ago, clusters_three_scans_ago, cluster_id)
                        if cluster_speed > 0:
                            relative_velocity = abs(cluster_speed - ego_velocity)
                        else:
                            relative_velocity = 0 # not known
                        
                        if (car_is_moving_toward_sensor 
                            and relative_velocity > velocity_threshold):
                            danger = {
                                "scan_number": scan_number,
                                "cluster_id": cluster_id,
                                "distance_sensor_longitudinal": minimal_distance_y,
                                "distance_sensor_lateral_dx": minimal_distance_dx,
                                "ego_velocity": ego_velocity,
                                "cluster_speed": cluster_speed,
                                "scenario": "overtaking"
                            }
                            dangerous_clusters.append(danger)
                        
                # safe overtaking/tailgating scenario with sufficeint distance or empty field of view 
                else: 
                    continue
        
    return dangerous_clusters

    

