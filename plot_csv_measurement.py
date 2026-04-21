# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import configurations as config
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

filepath_r = os.path.join(measurement_dir, "scan.csv")
filepath_xy = os.path.join(measurement_dir, "scan_xy.csv")

def playback_lidar():

    plt.ion()

    data = []

    # xy.csv einlesen: (timestamp, x, y)
    with open(filepath_xy, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            data.append((float(row[0]), float(row[1]), float(row[2])))

    if len(data) == 0:
        print("Keine Daten gefunden")
        return

    # Alle Timestamps sammeln (Frames)
    timestamps = [t for t, _, _ in data]
    unique_timestamps = list(dict.fromkeys(timestamps))

    print("Number of frames:", len(unique_timestamps))

    fig, ax = plt.subplots()

    for ts in unique_timestamps:

        x_vals = []
        y_vals = []

        # Alle Punkte mit gleichem Timestamp sammeln
        for t, x, y in data:
            if abs(t - ts) < 0.0001:
                x_vals.append(x)
                y_vals.append(y)

        x = np.array(x_vals)
        y = np.array(y_vals)

        if len(x) == 0:
            continue

        ax.clear()
        ax.scatter(x, y, s=2)

        ax.scatter(0, 0, color="red", s=20)

        ax.set_title("LiDAR Playback (XY)")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")

        ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
        ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)

        ax.set_aspect("equal")

        plt.pause(0.001)

    print("Playback done")


def plot_5_scans_r(filename, start_scan, points_per_scan=811):

    values = []

    with open(filename, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            values.append(float(row[2]))

    start_index = start_scan * points_per_scan

    plt.figure()

    for i in range(5):
        scan_start = start_index + i * points_per_scan
        scan_end = scan_start + points_per_scan

        scan_values = values[scan_start:scan_end]

        plt.plot(scan_values, label=f"Scan {start_scan + i}")

    plt.title("5 Consecutive Scans")
    plt.xlabel("Point Index")
    plt.ylabel("Distance (r)")
    plt.legend()
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

    # ? Daten nach Timestamp gruppieren
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

# playback_lidar()
# plot_5_scans_r(filepath_r, 100)
plot_5_scans_xy(filepath_xy, 50)
