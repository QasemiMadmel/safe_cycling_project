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
from get_velocities import getXandYVelocities
from save_measurement import save_median_and_ego_velocity_estimation
from save_measurement import save_rssi
from filename_handler import create_filename
from detectMovingObject import detectDanger
from detectMovingObject import detectTailgating
from ultrasoundsensor import UltrasoundReader
from ultrasound_thread import UltrasoundThread

# global variable: to stop program with a shortcut
running = True

# filepath for median values
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_median = create_filename(BASE_DIR, "median_and_ego_velocity", config.suffix)
filepath_rssi = create_filename(BASE_DIR, "rssi", config.suffix)
filepath_ultrasound = create_filename(BASE_DIR, "ultrasound", config.suffix)

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
    us_thread = None

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
            rssi = scan["rssi"]
            t_log = scan["t_log"]
        
        # thread starts acquiring data from the ultrasound sensor 
        us_thread = UltrasoundThread(filepath_ultrasound)
        us_thread.start()
        
        us_distance = us_thread.latest_distance
        previousUsTimestamp = None       
                
        # make a copy of the values
        previousValuesX = x.copy()
        previousValuesY = y.copy()
        previousTimestamp = timestamp
        previousMedian = 0                                              # set the median for first scan to zero 
        alpha = 0.1
        beta = 1 - alpha 

        save_rssi(filepath_rssi, rssi, t_log)                           # save the intensity values for the first scan
        
        # create a plot: 
        plt.ion()                                                       # interactive mode
        fig, ax = plt.subplots()                                        # create a figure and the axes
        colors = np.full(len(x), "blue", dtype=object)                  # create an array of colors for the points (default color is blue)
        sc = ax.scatter(x, y, s=2, c=colors)                            # give scatter the x and y coordinates, point size 2 and the color array
        ax.set_aspect('equal')                                          # both axes should remain equal
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          # set axis limit
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)          # set axis limit
        sc.set_color(colors)                                            # set colors array for visualization of areas and velocity direction 

        us_distances = []
        
        # while running variable is true
        while running:
            
            # get the next scan 
            scan = lidar_thread.latest_scan
            
            if scan is None: 
                continue
            
            r = scan["r"]
            x = scan["x"]
            y = scan["y"]
            timestamp = scan["timestamp"]
            rssi = scan["rssi"]
            t_log = scan["t_log"]
            
            if timestamp <= previousTimestamp:
                continue
            
            us_distance = us_thread.latest_distance
            currentUsTimestamp = us_thread.latest_timestamp
            
            if currentUsTimestamp != previousUsTimestamp:              
                us_distances.append(us_distance)
                
                if len(us_distances) > 5:
                    us_distances.pop(0)
                previousUsTimestamp = currentUsTimestamp
            
            # store the results
            currentX = x
            currentY = y
            
            # calculate the time between two consecutive scans 
            dt = (timestamp - previousTimestamp) / 1e6
            
            # do not divide by zero
            if dt <= 0:
                continue
            
            # calculate the velocity and its direction (via angle) 
            vx, vy, v = getXandYVelocities(previousValuesX, currentX, previousValuesY, currentY, dt, timestamp)
            
            # the median of the velocity for right measurment area:
            v_right = v[0:212]
            r_right = r[0:212]
            rssi_right = rssi[0:212]
   
            # calculate median of the velocity for the right side of the sensor 
            current_median_right_area = np.nanmedian(v_right)
            
            if np.isnan(current_median_right_area):
               current_median_right_area = previousMedian
               
            # alpha filter for an estimation of ego motion velocity
            ego_velocity_estimation = alpha * current_median_right_area + beta * previousMedian  # threshold for detection of moving object
            
            # detect potential danger
            overtakingObject = detectDanger(v_right, r_right, rssi_right, ego_velocity_estimation)
            
            # detect tailgaters
            tailgatingObject = detectTailgating(us_distances, ego_velocity_estimation)
            
            if tailgatingObject:
                print("Tailgating danger detected")
                
            # reset all colors to blue
            colors = np.full(len(x), "blue", dtype=object)
            
            # paint danger in red
            colors[overtakingObject] = "red"
            
            # save values in a file
            save_median_and_ego_velocity_estimation(filepath_median, timestamp, current_median_right_area, ego_velocity_estimation)             # save median values
            save_rssi(filepath_rssi, rssi, t_log)                       # save all rssi values 
            
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

    finally:
        print("Cleaning up and exiting...")
        if us_thread is not None: 
            us_thread.stop()
            us_thread.join(timeout=1)
        if lidar_thread is not None: 
            lidar_thread.stop()
            lidar_thread.join(timeout=1)
        plt.close('all')
        sys.exit(0)

if __name__ == "__main__":
    main()
