# main.py

import os
import signal
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from lidar_thread import LidarThread
from get_velocities import get_x_y_velocities
from save_measurement import save_ego_velocity
from filename_handler import create_filename
from detect_moving_object import detect_danger
import traceback

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
                
        previousUsTimestamp = None       
                
        # make a copy of the values
        previousValuesX = x.copy()
        previousValuesY = y.copy()
        previousTimestamp = timestamp
        previousMedian = 0                                              # set the median for first scan to zero 
        alpha = 0.1
        beta = 1 - alpha 
        
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
            
            if timestamp <= previousTimestamp:
                continue
            
            # store the results
            currentX = x
            currentY = y
            
            # calculate the time between two consecutive scans 
            dt = (timestamp - previousTimestamp) / 1e6
            
            # do not divide by zero
            if dt <= 0:
                continue
            
            # calculate the velocity and its direction (via angle) 
            vx, vy, v = get_x_y_velocities(previousValuesX, currentX, previousValuesY, currentY, dt, timestamp)
            
            # the median of the velocity for right measurment area:
            v_right = v[0:212]
            r_right = r[0:212]
   
            # calculate median of the velocity for the right side of the sensor 
            current_median_right_area = np.nanmedian(v_right)
            
            if np.isnan(current_median_right_area):
               current_median_right_area = previousMedian
               
            # alpha filter for an estimation of ego motion velocity
            ego_velocity_estimation = alpha * current_median_right_area + beta * previousMedian  # estimation of own velocity
            
            # detect potential danger
            overtakingObject = detect_danger(v_right, r_right, ego_velocity_estimation)
            
            # reset all colors to blue
            colors = np.full(len(x), "blue", dtype=object)
            
            # paint danger in red
            colors[overtakingObject] = "red"
            
            # save values in a file
            save_ego_velocity(filepath_ego_velocity, timestamp, ego_velocity_estimation)              # save median values
            
            # join x and y values into Nx2 array for plotting ([x1,y1], [x2,y2], [x3,y3]...) 
            sc.set_offsets(np.column_stack((x, y)))
            
            # set the colors
            sc.set_color(colors) 
            
            # pause to see the plot transformation (animation effect)
            plt.pause(0.001)

            # set the current scan as previous for next calculations 
            previousValuesX = currentX.copy()
            previousValuesY = currentY.copy()
            previousTimestamp = timestamp
            previousMedian = ego_velocity_estimation

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
