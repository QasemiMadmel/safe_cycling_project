# plot_csv_measurement.py

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import configurations as config

from filename_handler import create_filename_for_playbacks
from extract_points_in_critical_area import extract_points_in_critical_area
from clustering import find_segments
from clustering import merge_segments_into_clusters
from tracking import track_clusters
from tracking import set_default_id
from plot_clusters import plot_clusters
from detect_danger import distiguish_scenario_and_detect_danger
from save_measurement import save_dangerous_events

# NEW
from compute_ego_acceleration import compute_ego_acceleration
from verify_braking import verify_braking


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")


# ============================================================
# ADJUST THESE FILENAMES
# ============================================================

filepath_xy = os.path.join(
    measurement_dir,
    "01092026_scan_xy_recording_192125.csv"
)

filepath_ego_velocity = os.path.join(
    measurement_dir,
    "01092026_velocities_x_y_recording_192125.csv"
)

filepath_dangerous_events_playback = create_filename_for_playbacks(
    BASE_DIR,
    "danger_event_in",
    "recording",
    "01092026_192125"
)


# ============================================================
# LOAD XY DATA
# ============================================================

def load_xy_scans(filepath, points_per_scan=421):

    x_all = []
    y_all = []
    t_all = []

    with open(filepath, "r") as f:

        reader = csv.reader(f)

        for row in reader:

            if len(row) < 3:
                continue

            try:
                t_all.append(float(row[0]))
                x_all.append(float(row[1]))
                y_all.append(float(row[2]))

            except ValueError:
                continue


    t_all = np.array(t_all)
    x_all = np.array(x_all)
    y_all = np.array(y_all)


    num_frames = len(x_all) // points_per_scan


    t_all = t_all[:num_frames * points_per_scan]
    x_all = x_all[:num_frames * points_per_scan]
    y_all = y_all[:num_frames * points_per_scan]


    t_scans = t_all.reshape(num_frames, points_per_scan)
    x_scans = x_all.reshape(num_frames, points_per_scan)
    y_scans = y_all.reshape(num_frames, points_per_scan)


    return t_scans, x_scans, y_scans


# ============================================================
# LOAD SAVED EGO VELOCITIES
# ============================================================

def load_ego_velocities(filepath):

    ego_velocities = []

    with open(filepath, "r") as f:

        reader = csv.reader(f)

        for row in reader:

            if len(row) < 2:
                continue

            try:
                ego_velocities.append(float(row[1]))

            except ValueError:
                continue


    return ego_velocities


# ============================================================
# PLAYBACK
# ============================================================

def playback_lidar_with_tracking():

    points_per_scan = 421


    # --------------------------------------------------------
    # LOAD MEASUREMENT
    # --------------------------------------------------------

    t_scans, x_scans, y_scans = load_xy_scans(
        filepath_xy,
        points_per_scan
    )

    ego_velocities = load_ego_velocities(
        filepath_ego_velocity
    )


    if len(x_scans) == 0:

        print("No data found")
        return


    # --------------------------------------------------------
    # TRACKING INITIALIZATION
    # --------------------------------------------------------

    next_id = 1

    got_four_scans = False
    count = 0


    clusters_previous_scan = []
    clusters_two_scans_ago = []
    clusters_three_scans_ago = []


    # --------------------------------------------------------
    # NEW:
    # VARIABLES FOR ACCELERATION / BRAKING
    # --------------------------------------------------------

    previous_ego_velocity = None

    ego_acceleration_list = []

    braking_condition = False


    # --------------------------------------------------------
    # PLOT
    # --------------------------------------------------------

    plt.ion()

    fig, ax = plt.subplots()


    # --------------------------------------------------------
    # GO THROUGH ALL SCANS
    # --------------------------------------------------------

    for scan_index in range(len(x_scans) - 1):


        # ====================================================
        # GET CURRENT SCAN
        # ====================================================

        x = x_scans[scan_index]
        y = y_scans[scan_index]

        num_scan = scan_index


        # same dt as previously used in playback
        dt = (
            t_scans[scan_index + 1][0]
            - t_scans[scan_index][0]
        )


        if dt <= 0:
            continue


        # ====================================================
        # GET STORED EGO VELOCITY
        # ====================================================

        if scan_index < len(ego_velocities):

            ego_velocity_estimation = ego_velocities[scan_index]

        else:

            ego_velocity_estimation = 0.0


        # ====================================================
        # NEW:
        # COMPUTE EGO ACCELERATION FROM STORED VELOCITIES
        # ====================================================

        if previous_ego_velocity is None:

            ego_acceleration = None
            braking_condition = False

        else:

            ego_acceleration = compute_ego_acceleration(
                previous_ego_velocity,
                ego_velocity_estimation,
                dt
            )


            ego_acceleration_list, braking_condition = verify_braking(
                ego_acceleration_list,
                ego_acceleration
            )


        # ====================================================
        # CRITICAL AREA
        # ====================================================

        critical_x, critical_y = extract_points_in_critical_area(
            x,
            y
        )


        # ====================================================
        # SEGMENTATION
        # ====================================================

        segments_current_scan = find_segments(
            critical_x,
            critical_y,
            num_scan
        )


        clusters_current_scan = merge_segments_into_clusters(
            segments_current_scan
        )


        # ====================================================
        # TRACKING
        # ====================================================

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
                    next_id,
                    dt
                )


            else:

                clusters_current_scan_tracked = clusters_current_scan


                next_id = set_default_id(
                    clusters_current_scan_tracked,
                    next_id
                )


        # ====================================================
        # DANGER DETECTION
        # ====================================================

        if got_four_scans:

            danger = distiguish_scenario_and_detect_danger(
                ego_velocity_estimation,
                num_scan,
                clusters_current_scan_tracked,
                clusters_previous_scan,
                clusters_two_scans_ago,
                clusters_three_scans_ago,
                braking_condition,
                ego_acceleration
            )


            if len(danger) > 0:

                save_dangerous_events(
                    filepath_dangerous_events_playback,
                    danger
                )


        else:

            danger = []


        # ====================================================
        # PLOT
        # ====================================================

        plot_clusters(
            ax,
            x,
            y,
            clusters_current_scan_tracked,
            danger,
            config.PLOT_X_LIMIT,
            config.PLOT_Y_LIMIT
        )
        # lateral distance threshold dx = 2 m
        ax.axvline(
        x=1.5,
        color="red",
        linestyle="--",
        linewidth=2
        )

        # show acceleration / braking condition in title
        if ego_acceleration is None:

            acceleration_text = "None"

        else:

            acceleration_text = f"{ego_acceleration:.2f} m/s²"


        ax.set_title(
            f"CSV Playback - Scan {scan_index}\n"
            f"v = {ego_velocity_estimation:.2f} m/s | "
            f"a = {acceleration_text} | "
            f"Braking = {braking_condition}"
        )


        plt.pause(0.02)


        # ====================================================
        # SAVE CURRENT VALUES FOR NEXT SCAN
        # ====================================================

        clusters_three_scans_ago = clusters_two_scans_ago
        clusters_two_scans_ago = clusters_previous_scan
        clusters_previous_scan = clusters_current_scan_tracked


        # IMPORTANT:
        # only update AFTER acceleration was calculated
        previous_ego_velocity = ego_velocity_estimation


        # ====================================================
        # START TRACKING AFTER ENOUGH SCANS
        # ====================================================

        if got_four_scans is False:

            count += 1


        if count >= 3:

            got_four_scans = True


    print("Playback done")


    plt.ioff()
    plt.show()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    playback_lidar_with_tracking()
