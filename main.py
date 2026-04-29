# main.py

import signal
import sys
import numpy as np
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from get_velocities import getXandYVelocities
from classify_velocity import classify_velocity_direction

# global variable: to stop program with a shortcut
running = True

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

    # create a null object (safty)
    lidar = None

    try:
        
        # initialze lidar object
        lidar = LidarReader()
        
        # get one scan
        r, x, y, t_log, timestamp = lidar.getScan()
        
        # make a copy of the values
        previousScan = r.copy()
        previousValuesX = x.copy()
        previousValuesY = y.copy()
        previousTimestamp = timestamp
        
        # create a plot: 
        plt.ion()                                                       # interactive mode
        fig, ax = plt.subplots()                                        # create a figure and the axes
        colors = np.full(len(x), "blue", dtype=object)                  # create an array of colors for the points (default color is blue)
        colors[lidar.right] = "green"                                   # right side of the sensor should appear in green
        colors[lidar.front] = "orange"                                  # sensor front side is orange
        colors[lidar.left] = "magenta"                                  # left side is magenta
        sc = ax.scatter(x, y, s=2, c=colors)                            # give scatter the x and y cordinates, point size 2 and the color array
        ax.set_aspect('equal')                                          # both axes should remain equal
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          # set limits to both axes and set the "colors" array to visualize points in color
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)
        sc.set_color(colors)

        # while running variable is true
        while running:
            
            # get the next scan 
            r, x, y, t_log, timestamp = lidar.getScan()
            
            # store the results
            currentScan = r
            currentX = x
            currentY = y
            
            # calculate the time between two consecutive scans 
            dt = (timestamp - previousTimestamp) / 1e9
            
            # do not divide to zero
            if dt <= 0:
                continue
            
            # calculate the velocity and its direction through the angle of the vector 
            vx, vy, theta = getXandYVelocities( previousValuesX, currentX, previousValuesY, currentY, dt, timestamp)
            
            # visualize the points that are directed to the sensor in red!  
            colors = classify_velocity_direction(theta, lidar.right, lidar.front, lidar.left)
            
            # join x and y values in ([x1,y1], [x2,y2], [x3,y3]...) format and give them into the plot
            sc.set_offsets(np.column_stack((x, y)))
            
            # set the colors
            sc.set_color(colors) 
            
            # pasue to see the plot transformation (animation effect)
            plt.pause(0.001)

            # set the current scan as previous for next calculations 
            previousScan = currentScan.copy()
            previousValuesX = currentX.copy()
            previousValuesY = currentY.copy()
            previousTimestamp = timestamp

    # handle keyboardinterrupt to stop the program 
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping...")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Cleaning up and exiting...")
        plt.close('all')
        sys.exit(0)

if __name__ == "__main__":
    main()
