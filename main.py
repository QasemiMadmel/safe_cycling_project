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
from tracking import track_clusters_between_scans

# global variable: to stop program with a shortcut
running = True

# filepath for ego velocity
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_ego_velocity = create_filename(BASE_DIR, "ego_velocity", config.suffix)

def stop_handler(signum, frame):
    
    # global 
    global running 
    
    # control + c 
    print(f"Stop signal received: {signum}")  
   
    # set the variable to false to stop running 
    running = False

def main():
    
    # global variable to control the flow of the program 
    global running

    # signal function ...
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    # initialize variable (safety)
    lidar_thread = None

    try:
        # thread for lidar data acquisition
        lidar_thread = LidarThread()
        lidar_thread.start()
        
        
        cluster_colors = [
            "red",
            "green",
            "cyan",
            "magenta",
            "yellow",
            "black",
            "orange",
            "purple"
        ]
        
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
                
        # make a copy of the values
        previous_x_values = x.copy()
        previous_y_values = y.copy()
        previous_timestamp = timestamp
        previous_scan_count = num_scan
        previous_median = 0                                             # set the median for first scan to zero 
        alpha = 0.1
        beta = 1 - alpha 
        
        critical_x_previous, critical_y_previous = extract_points_in_critical_area(previous_x_values, previous_y_values)
        segments_previous_scan = cluster_segments(critical_x_previous, critical_y_previous, num_scan)
        clusters_previous_scan = merge_segments_into_clusters(segments_previous_scan)
        clusters_two_scans_ago = []
        clusters_three_scans_ago = []
        
        next_id = 1
        for cluster in clusters_previous_scan:
            cluster["id"] = next_id
            next_id += 1
        
        # create a plot: 
        plt.ion()                                                       # interactive mode
        fig, ax = plt.subplots()                                        # create a figure and the axes
        colors = np.full(len(x), "blue", dtype=object)                  # create an array of colors for the points (default color is blue)
        sc = ax.scatter(x, y, s=2, c=colors)                            # give scatter the x and y coordinates, point size 2 and the color array
        ax.set_aspect('equal')                                          # both axes should remain equal
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          # set axis limit
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)          # set axis limit
        sc.set_color(colors)                                            # set colors array for visualization of areas and velocity direction 

  
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
            
            # store the results
            current_x = x
            current_y = y
            
            # extract points in the area close to sensor
            critical_x_current, critical_y_current = extract_points_in_critical_area(current_x, current_y)
            
            # use neighbouring points to build segments in ecah scan and merge them into clusters if they are close to each other
            segments_current_scan = cluster_segments(critical_x_current, critical_y_current, scan_num_current)
            clusters_current_scan = merge_segments_into_clusters(segments_current_scan)
            clusters_current_scan_with_id, match_found = track_clusters(clusters_previous_scan, clusters_current_scan)
            
            if match_found == False
                clusters_with_id, match_found = track_clusters(clusters_two_scans_ago, clusters_current_scan)               
                if match_found == False 
                    clusters_with_id, match_found = track_clusters(clusters_three_scans_ago, clusters_current_scan)                
                    
            for cluster in clusters_current_scan:
                cluster["id"] = next_id 
                next_id += 1
            
            # calculate the time between two consecutive scans 
            dt = (timestamp - previous_timestamp) / 1e6
            
            # do not divide by zero
            if dt <= 0:
                continue
            
            # calculate the velocity and its direction (via angle) 
            vx, vy, v = get_x_y_velocities(previous_x_values, current_x, previous_y_values, current_y, dt, timestamp)
            
            # the median of the velocity for right measurment area:
            v_right = v[0:212]
            r_right = r[0:212]
   
            # calculate median of the velocity for the right side of the sensor 
            current_median_right_area = np.nanmedian(v_right)
            
            if np.isnan(current_median_right_area):
               current_median_right_area = previous_median
               
            # alpha filter for an estimation of ego motion velocity
            ego_velocity_estimation = alpha * current_median_right_area + beta * previous_median  # estimation of own velocity
                        
            # reset all colors to blue
            colors = np.full(len(x), "blue", dtype=object)
        
            # save values in a file
            save_ego_velocity(filepath_ego_velocity, timestamp, ego_velocity_estimation)              # save median values
            
            # join x and y values into Nx2 array for plotting ([x1,y1], [x2,y2], [x3,y3]...) 
            sc.set_offsets(np.column_stack((x, y)))
            
            # set the colors
            sc.set_color(colors) 
            
            ax.clear()
            ax.scatter(x, y, s= 2, c="blue")
            
            # paint clusters
            for idx, cluster in enumerate(clusters_current_scan):

                color = cluster_colors[
                idx % len(cluster_colors)
                ]

                ax.scatter(
                cluster["x"],
                cluster["y"],
                s=20,
                c=color
                )
            ax.set_aspect("equal")
            ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
            ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)
            
            # pause to see the plot transformation (animation effect)
            plt.pause(0.001)

            # set the current scan as previous for next calculations 
            previous_x_values = current_x.copy()
            previous_y_values = current_y.copy()
            previous_timestamp = timestamp
            previous_median = ego_velocity_estimation
            clusters_three_scans_ago = clusters_two_scans_ago
            clusters_two_scans_ago = clusters_previous_scan
            clusters_previous_scan = clusters_current_scan_with_id


    # handle keyboardinterrupt to stop the program 
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
