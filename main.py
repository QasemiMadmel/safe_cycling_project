# main.py

import os
import signal
import sys
import time
import threading
import numpy as np
import traceback
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from lidar_thread import LidarThread
from filename_handler import create_filename
from compute_ego_velocity import compute_ego_velocity
from compute_ego_acceleration import compute_ego_acceleration
from verify_braking import verify_braking
from extract_points_in_critical_area import extract_points_in_critical_area
from clustering import find_segments
from clustering import merge_segments_into_clusters
from tracking import track_clusters
from tracking import set_default_id
from detect_danger import distiguish_scenario_and_detect_danger
from issue_warning import issue_warning
from plot_clusters import plot_clusters
from save_measurement import save_ego_velocity
from save_measurement import save_dangerous_events



# global variable to control the flow of the program
running = True

# find the directory of the project and create filepath to store results of ego-velocity estimations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_ego_velocity = create_filename(BASE_DIR, "ego_velocity", config.suffix)
filepath_dangerous_events_live_measurement = create_filename(BASE_DIR, "danger_detected", config.suffix)

# function to stop measurement on "control+c"
def stop_handler(signum, frame):
    
    global running 
    print(f"Stop signal received: {signum}")  
    running = False

def main():
    
    start_time = time.monotonic()
    global running
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    
    # initialization of a thread that handles data acquistion 
    lidar_thread = None
    
    # creating an event object 
    danger_event = threading.Event()
    stop_event = threading.Event()
    
    # an extra thread get the task to issue a warning and sets the predefined events 
    warning_thread = threading.Thread(target=issue_warning,args=(danger_event, stop_event), name="Warning_Thread")
 
    try:
        
        # create a lidarThread object and start thread to start the measurement
        lidar_thread = LidarThread()
        lidar_thread.start()
        
        # start the second thread that sets danger_event and stops it based on the results from processing 
        warning_thread.start()
        
        # waite for data (15 Hz: 0.066s)
        while lidar_thread.latest_scan is None: 
            time.sleep(0.01)
            
        # store the first scan
        scan = lidar_thread.latest_scan
        # extract data from scan
        if scan is not None:
            r = scan["r"]
            x = scan["x"]
            y = scan["y"]
            timestamp = scan["timestamp"]
            t_log = scan["t_log"]
            num_scan = scan["scan_number"]
            
            scan["ego_velocity"] = None
            scan["ego_acceleration"] = None
            
            previous_ego_velocity = None 
            
         
        # store the first parameter of the scan    
        previous_x_values = x.copy()
        previous_y_values = y.copy()
        previous_timestamp = timestamp
        previous_scan_count = num_scan
        previous_median = 0                                             
        alpha = 0.1
        beta = 1 - alpha 
        
        # the code is designed to store the first four scans before tracking starts
        gotFourScans = False
        count = 0
        
        # extract points in the critical area for further processing
        critical_x_previous, critical_y_previous = extract_points_in_critical_area(previous_x_values, previous_y_values)
        
        # look for segments in the critical area based on the distances between points
        segments_previous_scan = find_segments(critical_x_previous, critical_y_previous, num_scan)
        
        # build clusters out of segments that belong togather 
        clusters_previous_scan = merge_segments_into_clusters(segments_previous_scan)
        
        # initialize empty directories to store multiple scans
        clusters_two_scans_ago = []
        clusters_three_scans_ago = []
        danger = [] # empty for the first three scans
        
        # keep track of the ego acceleration
        ego_acceleration_list = []
        braking_condition = False
        
        # give the first three scan-clusters id's as reference 
        next_id = 1
        for cluster in clusters_previous_scan:
            cluster["id"] = next_id
            next_id += 1
        
        # plot in interactive mode
        plt.ion()                                                       
        fig, ax = plt.subplots()                                       
        colors = np.full(len(x), "blue", dtype=object)                  
        sc = ax.scatter(x, y, s=2, c=colors)                            
        ax.set_aspect('equal')                                          
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)          
        sc.set_color(colors)                                            

        while running:
 
            # store the next scan and extract the informatoin after it is available
            with lidar_thread.lock:
                scan = lidar_thread.latest_scan
            
            if scan is None: 
                continue

            r = scan["r"]
            current_x = scan["x"]
            current_y = scan["y"]
            timestamp = scan["timestamp"]
            t_log = scan["t_log"]
            scan_num_current = scan["scan_number"]

            if timestamp <= previous_timestamp:
                continue
            
            # calculate the time in between scans
            dt = (timestamp - previous_timestamp) / 1e6
            
            if dt <= 0:
                continue
            
            # compute the velocities, take the median for ego velocity estimation and apply filter 
            ego_velocity_estimation = compute_ego_velocity(previous_median, previous_x_values, current_x, previous_y_values, current_y, dt, timestamp, alpha, beta)
            scan["ego_velocity"] = ego_velocity_estimation
            previous_ego_velocity = ego_velocity_estimation
            
            if previous_ego_velocity is None:
                ego_acceleration = None
                braking_condition = False

            else:
                ego_acceleration = compute_ego_acceleration(previous_ego_velocity, ego_velocity_estimation, dt)
                ego_acceleration_list, braking_condition = verify_braking(ego_acceleration_list, ego_acceleration)
            
            scan["ego_acceleration"] = ego_acceleration
            
            # store the values in a file 
            save_ego_velocity(filepath_ego_velocity, timestamp, ego_velocity_estimation) 
             
            # in order to track clusters, process the scans incoming: 1. extract points in area close to sensor 
            critical_x_current, critical_y_current = extract_points_in_critical_area(current_x, current_y)
            
            # build segments out of neighbouring points
            segments_current_scan = find_segments(critical_x_current, critical_y_current, scan_num_current)
            
            # merge segments close to each other into clusters
            clusters_current_scan = merge_segments_into_clusters(segments_current_scan)
            
            # start tracking after the minimum number of 4 stored scans, otherwise get/store next ones and set default cluster_id's 
            if gotFourScans:
                # start tracking
                clusters_current_scan_tracked, next_id = track_clusters(clusters_three_scans_ago,
                                                                        clusters_two_scans_ago,
                                                                        clusters_previous_scan,
                                                                        clusters_current_scan, 
                                                                        next_id,
                                                                        dt)
                # danger detection                                                        
                danger = distiguish_scenario_and_detect_danger(ego_velocity_estimation, 
                        scan_num_current,
                        clusters_current_scan_tracked,
                        clusters_previous_scan,
                        clusters_two_scans_ago,
                        clusters_three_scans_ago, 
                        braking_condition, 
                        ego_acceleration)
                if danger:
                    danger_event.set() # sets an event that triggers warning if a dangerous event occurs
                    save_dangerous_events(filepath_dangerous_events_live_measurement, danger)
            
            else:
                # simply save scan as tracked until the first four scans are stored 
                clusters_current_scan_tracked = clusters_current_scan
                next_id = set_default_id(clusters_current_scan_tracked, next_id)   
            
            # plot the measurement
            plot_clusters(ax, current_x, current_y, clusters_current_scan_tracked, danger, config.PLOT_X_LIMIT, config.PLOT_Y_LIMIT)
            
            # pause in between scans for animation effect
            plt.pause(0.001)
    
            # store current values as previous for the next round of loop 
            previous_x_values = current_x.copy() 
            previous_y_values = current_y.copy()
            previous_timestamp = timestamp
            previous_median = ego_velocity_estimation
            clusters_three_scans_ago = clusters_two_scans_ago
            clusters_two_scans_ago = clusters_previous_scan
            clusters_previous_scan = clusters_current_scan_tracked
            
            # logic to start tracking after 4 scans have been received
            if gotFourScans is False:
                count += 1
            if count >= 3:
                gotFourScans =True

    # following section handles exceptions, stops the measurment on keyboardInterrupt and display errors
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping...")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    finally:
        
        end_time = time.monotonic()
        measurement_duration = end_time - start_time
        print("Measurement duration in seconds: " ,measurement_duration)
        
        stop_event.set() # ends the waiting condition of warning thread
        
        # wakes the thread that is waiting (danger_event.wait()) to verify wethear stop_event is set
        danger_event.set()  
        
        if warning_thread.is_alive():
            warning_thread.join(timeout=2.0)
            
        print("Cleaning up and exiting...")
        
        if lidar_thread is not None: 
            lidar_thread.stop()
            lidar_thread.join(timeout=1)
        
        plt.close('all')
        sys.exit(0)

if __name__ == "__main__":
    main()
