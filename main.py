# main.py

import os
import signal
import sys
import time
import numpy as np
import traceback
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from lidar_thread import LidarThread
from get_velocities import get_x_y_velocities
from save_measurement import save_ego_velocity
from filename_handler import create_filename
from detect_moving_object import detect_danger
from extract_points_in_critical_area import extract_points_in_critical_area
from clustering import cluster_segments
from clustering import merge_segments_into_clusters
from tracking import track_clusters
from plot_clusters import plot_clusters

running = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_ego_velocity = create_filename(BASE_DIR, "ego_velocity", config.suffix)

def stop_handler(signum, frame):
    
    global running 
    print(f"Stop signal received: {signum}")  
    running = False

def main():
    
    global running

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    lidar_thread = None

    try:
        lidar_thread = LidarThread()
        lidar_thread.start()
        
        
        cluster_colors = ["red", "green", "cyan", "magenta", "yellow", "black", "orange", "purple"]
        
        while lidar_thread.latest_scan is None: 
            time.sleep(0.01)
            
        # get one scan
        scan = lidar_thread.latest_scan
            
        if scan is not None:
            r = scan["r"]
            x = scan["x"]
            y = scan["y"]
            timestamp = scan["timestamp"]
            t_log = scan["t_log"]
            num_scan = scan["scan_number"]
                
        previousUsTimestamp = None       
        previous_x_values = x.copy()
        previous_y_values = y.copy()
        previous_timestamp = timestamp
        previous_scan_count = num_scan
        previous_median = 0                                             
        alpha = 0.1
        beta = 1 - alpha 
        
        gotFourScans = False
        count = 0
        
        critical_x_previous, critical_y_previous = extract_points_in_critical_area(previous_x_values, previous_y_values)
        segments_previous_scan = cluster_segments(critical_x_previous, critical_y_previous, num_scan)
        clusters_previous_scan = merge_segments_into_clusters(segments_previous_scan)
        
        clusters_two_scans_ago = []
        clusters_three_scans_ago = []
        
        next_id = 1
        for cluster in clusters_previous_scan:
            cluster["id"] = next_id
            next_id += 1
        
        plt.ion()                                                       
        fig, ax = plt.subplots()                                       
        colors = np.full(len(x), "blue", dtype=object)                  
        sc = ax.scatter(x, y, s=2, c=colors)                            
        ax.set_aspect('equal')                                          
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)          
        sc.set_color(colors)                                            


        while running:
            
            # get the next scan 
            scan = lidar_thread.latest_scan
            
            if scan is None: 
                continue
            
            r = scan["r"]
            x = scan["x"]
            y = scan["y"]
            timestamp = scan["timestamp"]
            t_log = scan["t_log"]
            scan_num_current = scan["scan_number"]
            
            if timestamp <= previous_timestamp:
                continue
            

            current_x = x
            current_y = y
            
 
            critical_x_current, critical_y_current = extract_points_in_critical_area(current_x, current_y)
            segments_current_scan = cluster_segments(critical_x_current, critical_y_current, scan_num_current)
            clusters_current_scan = merge_segments_into_clusters(segments_current_scan)
            
            clusters_current_scan_tracked = clusters_current_scan
            if gotFourScans is True:
                clusters_current_scan_tracked, next_id = track_clusters(clusters_three_scans_ago,
                                                                        clusters_two_scans_ago,
                                                                        clusters_previous_scan,
                                                                        clusters_current_scan, 
                                                                        next_id)
            

            dt = (timestamp - previous_timestamp) / 1e6
            
            if dt <= 0:
                continue
            
            vx, vy, v = get_x_y_velocities(previous_x_values, current_x, previous_y_values, current_y, dt, timestamp)

            v_right = v[0:212]
            r_right = r[0:212]
   
            current_median_right_area = np.nanmedian(v_right)
            
            if np.isnan(current_median_right_area):
               current_median_right_area = previous_median
               
            ego_velocity_estimation = alpha * current_median_right_area + beta * previous_median  
            save_ego_velocity(filepath_ego_velocity, timestamp, ego_velocity_estimation) 

            
            colors = np.full(len(x), "blue", dtype=object)        
            sc.set_offsets(np.column_stack((x, y)))
            sc.set_color(colors) 
            plot_clusters(ax, x, y, clusters_current_scan_tracked, cluster_colors, config.PLOT_X_LIMIT, config.PLOT_Y_LIMIT)
            plt.pause(0.001)

            
            previous_x_values = current_x.copy()
            previous_y_values = current_y.copy()
            previous_timestamp = timestamp
            previous_median = ego_velocity_estimation
            clusters_three_scans_ago = clusters_two_scans_ago
            clusters_two_scans_ago = clusters_previous_scan
            clusters_previous_scan = clusters_current_scan_tracked
            
            if gotFourScans is False:
                count += 1
            if count >= 3:
                gotFourScans =True

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping...")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    finally:
        print("Cleaning up and exiting...")
        if lidar_thread is not None: 
            lidar_thread.stop()
            lidar_thread.join(timeout=1)
        plt.close('all')
        sys.exit(0)

if __name__ == "__main__":
    main()
