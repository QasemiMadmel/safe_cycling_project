# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import csv
import configurations as config
from detectMovingObject import detectDanger
import os 

# define paths 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

# set filenames for plots (the file that contains xy coordinates as well as the one containing velocities and angles)

filepath_xy = os.path.join(measurement_dir,"24052026_scan_xy_tailgating_2.csv")
filepath_vel = os.path.join(measurement_dir,"24052026_velocities_x_y_tailgating_2.csv")
filepath_scan_r = os.path.join(measurement_dir,"24052026_scan_tailgating_2.csv")
filepath_rssi = os.path.join(measurement_dir,"24052026_rssi_tailgating_2.csv")
filepath_median_and_ego_velocity = os.path.join(measurement_dir,"24052026_median_and_ego_velocity_tailgating_2.csv")

def playback_lidar():

    # interactive mode 
    plt.ion()
    
    # arrays to store the data 
    xy_data = []
    v_data = []
    r_data = []
    rssi_data = []
    ego_velocity_data = []
    
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
            v = float(row[3])
            v_data.append(v)
    
    with open(filepath_scan_r, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            r = float(row[2])
            r_data.append(r)
        
    with open(filepath_rssi, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            rssi = float(row[1])
            rssi_data.append(rssi)
    
    with open(filepath_median_and_ego_velocity, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            ego_velocity = float(row[1])
            ego_velocity_data.append(ego_velocity)
    
    # check if the data arrays are empty 
    if len(xy_data) == 0 or len(v_data) == 0 or len(rssi_data) == 0 or len(ego_velocity_data) == 0:
        print("no data was found")
        return
    
    # number of points for a single scan if the view is limited 
    points_per_scan = 421
    
    # the number of scans stored for velocities are usually below the number of scans actually captured 
    # skip the first scan! (synchronizing data)
    xy_data = xy_data[points_per_scan:] 
    
    # get the length of the smaller array
    min_len = min(len(xy_data), len(v_data))
    
    # calculate the number of frames 
    num_frames = len(xy_data) // points_per_scan
    print("Number of frames:", num_frames)

    # cut to the minimum length
    xy_data = xy_data[:min_len]
    v_data = v_data[:min_len]
    ego_velocity_data = ego_velocity_data[:min_len]
    r_data = r_data[:min_len]
    rssi_data = rssi_data[:min_len]
    ego_velocity_data = ego_velocity_data[:num_frames]

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
        v = np.array(v_data[start:end])
        r = np.array(r_data[start:end])
        rssi = np.array(rssi_data[start:end])
        egoVel = ego_velocity_data[i]
        
        # check if data is empty
        if len(x) == 0 or len(v) == 0 or len(r) == 0 or len(rssi) == 0:
            continue
            
        v_right = v[0:212]
        r_right = r[0:212]
        rssi_right = rssi[0:212]
        
        overtakingCar = detectDanger(v_right, r_right, rssi_right, egoVel)

        # set parameters of the plot
        colors = np.full(len(x), "blue", dtype=object)
        colors[overtakingCar] = "red" 
        ax.clear()                                                      # clean up previous scan
        ax.scatter(x, y, s=20, c=colors)                                 # x, y and point size
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
        
playback_lidar()

