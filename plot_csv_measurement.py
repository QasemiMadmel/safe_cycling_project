# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import configurations as config
import os 
from collections import defaultdict
from classify_velocity import classify_velocity_direction_playback

# define paths 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

# set filenames for plots (the file that contains xy coordinates as well as the one containing velocities and angles)
filepath_xy = os.path.join(measurement_dir,"28042026_scan_xy_outdoor_riding_forward.csv")
filepath_vel = os.path.join(measurement_dir,"28042026_velocities_x_y_outdoor_riding_forward.csv")

def playback_lidar():

    # interactive mode 
    plt.ion()
    
    # arrays to store the data 
    xy_data = []
    theta_data = []

    # open both files in read mode and store data in both arrays:
    
    with open(filepath_xy, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            x = float(row[1])
            y = float(row[2])
            xy_data.append((x, y))


    with open(filepath_vel, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue
            theta = float(row[3])
            theta_data.append(theta)
    
    # check if the data arrays are empty 
    if len(xy_data) == 0 or len(theta_data) == 0:
        print("no data was found")
        return
    
    # number of points for a single scan if the view is limited 
    points_per_scan = 421
    
    # the number of scans stored for velocities are usually below the number of scans actually captured 
    # skip the first scan! (synchronizing data)
    xy_data = xy_data[points_per_scan:] 
    
    # get the length of the smaller array
    min_len = min(len(xy_data), len(theta_data))

    # cut to the minimum length
    xy_data = xy_data[:min_len]
    theta_data = theta_data[:min_len]

    # calculate the number of frames 
    num_frames = len(xy_data) // points_per_scan
    print("Number of frames:", num_frames)

    # create figure and axes
    fig, ax = plt.subplots()
    
    # for each frame
    for i in range(num_frames):

        # set the start and end index of the points based on the number of points available for a single scan 
        start = i * points_per_scan
        end = start + points_per_scan

        # extract x,y arrays from the current scan
        x = np.array([p[0] for p in xy_data[start:end]])
        y = np.array([p[1] for p in xy_data[start:end]])
        theta = np.array(theta_data[start:end])

        # check if data is empty
        if len(x) == 0:
            continue

        # function returns a color array that visualize right, front and left areas in dfferent 
        # colors and paints the point that are directed toward sensor in red 
        colors = classify_velocity_direction_playback(theta)

        # set parameters of the plot
        ax.clear()                                                      # clean up previous scan
        ax.scatter(x, y, s=2, c=colors)                                 # x, y and point size
        ax.scatter(0, 0, color="red", s=20)                             # plot the sensor itself in red 
        ax.set_title(f"LiDAR Playback (Frame {i})")                     # title
        ax.set_xlabel("x (m)")                                          # label x
        ax.set_ylabel("y (m)")                                          # label y
        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)          # set limit for x axis
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)          # set limit for y axis
        ax.set_aspect("equal")                                          # both axes should be equal
        plt.pause(0.03)                                                 # pause for animation effect

    print("Playback done")

    plt.ioff()                                                          # end of interactive mode
    plt.show()
    
def plot_5_scans_xy(filename, start_scan, points_per_scan=421):         # points per scan can be set to 811 (full fov) if all scan points were stored in data acquisition!

    # array for data storage
    data = []

    # open file to get the coordinates
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            data.append((float(row[0]), float(row[1]), float(row[2])))
     
    # check if the data is empty
    if len(data) == 0:
        print("no data was found")
        return
     
    # store in dictionary {s1: {[x1,y1], [x2, y2], [],... }, s2: {[], [], [],...}, s3: {[], [], [],...},..}
    scans = {}
    for t, x, y in data:
        
        if t not in scans:
            scans[t] = {"x": [], "y": []}
        
        scans[t]["x"].append(x)
        scans[t]["y"].append(y)

    # each scan has only one timestamp value which will be employed as key
    unique_timestamps = list(scans.keys())
    
    # create a figure
    plt.figure()
    
    # plot 5 consecutive scans 
    for i in range(5):
        
        # index of the first scan from function parameter
        idx = start_scan + i

        # check if it exceeds the number of scans
        if idx >= len(unique_timestamps):
            print("not enough scans available")
            break
        
        # get the timestamp of the first scan for the plot
        ts = unique_timestamps[idx]
        
        # use the timestamp (key) to access the coordinates
        scan = scans[ts]
        x_arr = np.array(scan["x"])
        y_arr = np.array(scan["y"])
        
        # check if scan is empty
        if len(x_arr) == 0:
            print("Scan incomplete")
            continue
        
        # plot the scan (in each iteration the new scans will be added to this plot)
        plt.scatter(x_arr, y_arr, s=5, label=f"Scan {idx}")

    # set the title and labels for the plot
    plt.title("5 Scans in XY Space")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.axis("equal")
    plt.legend()
    plt.show()

playback_lidar()
plot_5_scans_xy(filepath_xy, 40)
