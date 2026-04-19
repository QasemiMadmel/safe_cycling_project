# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import configurations as config

plt.ion()


angles = np.deg2rad(
    config.START_ANGLE + np.arange(config.DISTANCE_POINTS_COUNT) * config.STEP_ANGLE
)

data = []
with open("scan.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue
        data.append((float(row[0]), int(row[1]), float(row[2])))

if len(data) == 0:
    print("Keine Daten gefunden")
    exit()


timestamps = [t for t, _, _ in data]
unique_timestamps = list(dict.fromkeys(timestamps))

print("Anzahl Frames:", len(unique_timestamps))


fig, ax = plt.subplots()


for ts in unique_timestamps:

    r = []

    for t, i, d in data:
        if abs(t - ts) < 0.001:
            r.append(d)

    r = np.array(r)


    if len(r) != config.DISTANCE_POINTS_COUNT:
        continue


    x = r * np.cos(angles)
    y = r * np.sin(angles)


    ax.clear()
    ax.scatter(x, y, s=2)


    ax.scatter(0, 0, color="red", s=20)

    ax.set_title("LiDAR Playback")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")


    ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
    ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)

    ax.set_aspect("equal")

    plt.pause(0.01)  

print("Playback fertig")
