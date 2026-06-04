# plot_csv_measurement.py

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import configurations as config
from extract_points_in_critical_area import extract_points_in_critical_area
from clustering import cluster_segments
from clustering import merge_segments_into_clusters
from tracking import track_clusters
from tracking import set_default_id
from plot_clusters import plot_clusters


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")

filepath_xy = os.path.join(measurement_dir, "04062026_scan_xy_test.csv")


def load_xy_scans(filepath, points_per_scan=421):

    x_all = []
    y_all = []

    with open(filepath, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) < 3:
                continue

            try:
                x_all.append(float(row[1]))
                y_all.append(float(row[2]))
            except ValueError:
                continue

    x_all = np.array(x_all)
    y_all = np.array(y_all)

    num_frames = len(x_all) // points_per_scan

    x_all = x_all[:num_frames * points_per_scan]
    y_all = y_all[:num_frames * points_per_scan]

    x_scans = x_all.reshape(num_frames, points_per_scan)
    y_scans = y_all.reshape(num_frames, points_per_scan)

    return x_scans, y_scans


def playback_lidar_with_tracking():

    points_per_scan = 421

    x_scans, y_scans = load_xy_scans(filepath_xy, points_per_scan)

    if len(x_scans) == 0:
        print("No data found")
        return

    next_id = 1
    got_four_scans = False
    count = 0

    clusters_previous_scan = []
    clusters_two_scans_ago = []
    clusters_three_scans_ago = []

    plt.ion()
    fig, ax = plt.subplots()

    for scan_index in range(len(x_scans)):

        x = x_scans[scan_index]
        y = y_scans[scan_index]
        num_scan = scan_index

        critical_x, critical_y = extract_points_in_critical_area(x, y)
        segments_current_scan = cluster_segments(critical_x, critical_y, num_scan)
        clusters_current_scan = merge_segments_into_clusters(segments_current_scan)

        if scan_index == 0:
            for cluster in clusters_current_scan:
                cluster["id"] = next_id
                next_id += 1
            clusters_current_scan_tracked = clusters_current_scan
        else:
            if got_four_scans:
                clusters_current_scan_tracked, next_id = track_clusters(
                    clusters_three_scans_ago,
                    clusters_two_scans_ago,
                    clusters_previous_scan,
                    clusters_current_scan,
                    next_id)
            else:
                clusters_current_scan_tracked = clusters_current_scan
                next_id = set_default_id(clusters_current_scan_tracked, next_id)

        plot_clusters(ax, x, y, clusters_current_scan_tracked, config.PLOT_X_LIMIT, config.PLOT_Y_LIMIT)
        
        ax.set_title(f"CSV Playback with Tracking - Scan {scan_index}")
        plt.pause(0.03)

        clusters_three_scans_ago = clusters_two_scans_ago
        clusters_two_scans_ago = clusters_previous_scan
        clusters_previous_scan = clusters_current_scan_tracked

        if got_four_scans is False:
            count += 1

        if count >= 3:
            got_four_scans = True

    print("Playback done")

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    playback_lidar_with_tracking()
