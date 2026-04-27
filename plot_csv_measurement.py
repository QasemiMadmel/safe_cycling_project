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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

filepath_xy = os.path.join(measurement_dir, "27042026_scan_xy_test_backward_forward_slalom.csv")
filepath_vel = os.path.join(measurement_dir, "27042026_velocities_x_y_test_backward_forward_slalom.csv")

def playback_lidar():

    plt.ion()

    xy_data = []
    theta_data = []

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


    if len(xy_data) == 0 or len(theta_data) == 0:
        print("no data was found")
        return
    
    points_per_scan = 421
    xy_data = xy_data[points_per_scan:]
    min_len = min(len(xy_data), len(theta_data))

    xy_data = xy_data[:min_len]
    theta_data = theta_data[:min_len]


    points_per_scan = 421 
    num_frames = len(xy_data) // points_per_scan

    print("Number of frames:", num_frames)

    fig, ax = plt.subplots()

    for i in range(num_frames):

        start = i * points_per_scan
        end = start + points_per_scan

        x = np.array([p[0] for p in xy_data[start:end]])
        y = np.array([p[1] for p in xy_data[start:end]])
        theta = np.array(theta_data[start:end])

        if len(x) == 0:
            continue

        colors = classify_velocity_direction_playback(theta)


        ax.clear()
        ax.scatter(x, y, s=2, c=colors)
        ax.scatter(0, 0, color="red", s=20)

        ax.set_title(f"LiDAR Playback (Frame {i})")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")

        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)
        ax.set_aspect("equal")

        plt.pause(0.03)  

    print("Playback done")

    plt.ioff()
    plt.show()
    
def plot_5_scans_xy(filename, start_scan, points_per_scan=811):

    data = []

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            data.append((float(row[0]), float(row[1]), float(row[2])))

    if len(data) == 0:
        print("no data was found")
        return

    scans = {}
    for t, x, y in data:
        if t not in scans:
            scans[t] = {"x": [], "y": []}
        scans[t]["x"].append(x)
        scans[t]["y"].append(y)

    unique_timestamps = list(scans.keys())

    plt.figure()

    for i in range(5):
        idx = start_scan + i

        if idx >= len(unique_timestamps):
            print("not enough scans available")
            break

        ts = unique_timestamps[idx]
        scan = scans[ts]

        x_arr = np.array(scan["x"])
        y_arr = np.array(scan["y"])

        if len(x_arr) == 0:
            print("Scan incomplete")
            continue

        plt.scatter(x_arr, y_arr, s=5, label=f"Scan {idx}")

    plt.title("5 Scans in XY Space")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.axis("equal")
    plt.legend()
    plt.show()

playback_lidar()
#plot_5_scans_xy(filepath_xy, 50)
