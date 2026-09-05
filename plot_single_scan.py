# plot_single_scan_v2.py
#
# Improved version of plot_single_scan.py
# - processes all previous scans up to the target scan
# - only displays ONE selected scan
# - makes the upper text easier to read
# - creates more space above the plot
# - optionally shows the measurement info in a separate info box

import os
import sys
import csv
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

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

from compute_ego_acceleration import compute_ego_acceleration
from verify_braking import verify_braking


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")

TARGET_SCAN = 275
SAVE_DANGER_EVENTS = False

# NEW: plotting settings for better readability
FIG_WIDTH = 11
FIG_HEIGHT = 10
TITLE_FONT_SIZE = 10
INFO_FONT_SIZE = 16
TICK_FONT_SIZE = 14
LEGEND_FONT_SIZE = 15
CLUSTER_TEXT_MIN_SIZE = 18
USE_INFO_BOX_INSIDE_PLOT = True   # set False if you only want the title


# ============================================================
# ADJUST THESE FILENAMES
# ============================================================

filepath_xy = os.path.join(
    measurement_dir,
    "01092026_scan_xy_recording_184907.csv"
)

filepath_ego_velocity = os.path.join(
    measurement_dir,
    "01092026_velocities_x_y_recording_184907.csv"
)

filepath_dangerous_events_playback = create_filename_for_playbacks(
    BASE_DIR,
    "danger_event_in",
    "recording",
    "01092026_184907"
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
# MAKE IMPORTANT ANNOTATIONS LARGE
# ============================================================

def make_plot_annotations_large(ax):

    for text in ax.texts:
        current_size = text.get_fontsize()
        text.set_fontsize(max(current_size, CLUSTER_TEXT_MIN_SIZE))
        text.set_fontweight("bold")

    for patch in ax.patches:
        if isinstance(patch, FancyArrowPatch):
            patch.set_mutation_scale(30)
            patch.set_linewidth(3)


def add_large_danger_banner(ax, danger):

    if len(danger) > 0:
        ax.text(
            0.02,
            0.98,
            "DANGER",
            transform=ax.transAxes,
            fontsize=24,
            fontweight="bold",
            verticalalignment="top",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor="red",
                linewidth=3
            )
        )


def add_info_box(ax, target_scan, ego_velocity, ego_acceleration, braking_condition):

    if ego_acceleration is None:
        acceleration_text = "None"
    else:
        acceleration_text = f"{ego_acceleration:.2f} m/s²"

    info_text = (
        f"Scan: {target_scan}\n"
        f"v = {ego_velocity:.2f} m/s\n"
        f"a = {acceleration_text}\n"
        f"Braking = {braking_condition}"
    )

    ax.text(
        0.02,
        0.82,
        info_text,
        transform=ax.transAxes,
        fontsize=INFO_FONT_SIZE,
        fontweight="bold",
        verticalalignment="top",
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="white",
            edgecolor="black",
            linewidth=2,
            alpha=0.9
        )
    )


# ============================================================
# PROCESS MEASUREMENT AND PLOT ONLY ONE SCAN
# ============================================================

def plot_single_scan(target_scan):

    points_per_scan = 421

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

    max_valid_scan = len(x_scans) - 2

    if target_scan < 0 or target_scan > max_valid_scan:
        raise ValueError(
            f"TARGET_SCAN must be between 0 and {max_valid_scan}. "
            f"Requested: {target_scan}"
        )

    next_id = 1

    got_four_scans = False
    count = 0

    clusters_previous_scan = []
    clusters_two_scans_ago = []
    clusters_three_scans_ago = []

    previous_ego_velocity = None
    ego_acceleration_list = []
    braking_condition = False

    target_x = None
    target_y = None
    target_clusters = None
    target_danger = None
    target_ego_velocity = None
    target_ego_acceleration = None
    target_braking_condition = None

    for scan_index in range(target_scan + 1):

        x = x_scans[scan_index]
        y = y_scans[scan_index]

        num_scan = scan_index

        dt = (
            t_scans[scan_index + 1][0]
            - t_scans[scan_index][0]
        )

        if dt <= 0:
            print(f"Warning: scan {scan_index} skipped because dt <= 0")
            continue

        if scan_index < len(ego_velocities):
            ego_velocity_estimation = ego_velocities[scan_index]
        else:
            ego_velocity_estimation = 0.0

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

        critical_x, critical_y = extract_points_in_critical_area(
            x,
            y
        )

        segments_current_scan = find_segments(
            critical_x,
            critical_y,
            num_scan
        )

        clusters_current_scan = merge_segments_into_clusters(
            segments_current_scan
        )

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

            if SAVE_DANGER_EVENTS and len(danger) > 0:
                save_dangerous_events(
                    filepath_dangerous_events_playback,
                    danger
                )
        else:
            danger = []

        if scan_index == target_scan:
            target_x = x.copy()
            target_y = y.copy()
            target_clusters = clusters_current_scan_tracked
            target_danger = danger
            target_ego_velocity = ego_velocity_estimation
            target_ego_acceleration = ego_acceleration
            target_braking_condition = braking_condition

        clusters_three_scans_ago = clusters_two_scans_ago
        clusters_two_scans_ago = clusters_previous_scan
        clusters_previous_scan = clusters_current_scan_tracked

        previous_ego_velocity = ego_velocity_estimation

        if got_four_scans is False:
            count += 1

        if count >= 3:
            got_four_scans = True

    if target_x is None:
        print(f"Scan {target_scan} could not be processed.")
        return

    # ========================================================
    # IMPROVED PLOT LAYOUT
    # ========================================================

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))

    plot_clusters(
        ax,
        target_x,
        target_y,
        target_clusters,
        target_danger,
        config.PLOT_X_LIMIT,
        config.PLOT_Y_LIMIT
    )

    ax.axvline(
        x=1.5,
        color="red",
        linestyle="--",
        linewidth=3,
        label="1.5 m threshold"
    )

    make_plot_annotations_large(ax)
    add_large_danger_banner(ax, target_danger)

    if target_ego_acceleration is None:
        acceleration_text = "None"
    else:
        acceleration_text = f"{target_ego_acceleration:.2f} m/s²"

    # NEW:
    # Put the main info in a suptitle with enough space above the axes
    fig.suptitle(
        f"CSV Measurement - Scan {target_scan}",
        fontsize=TITLE_FONT_SIZE,
        fontweight="bold",
        y=0.86
    )


    ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
    ax.legend(fontsize=LEGEND_FONT_SIZE, loc="upper right")

    # leave extra room for the title
    fig.subplots_adjust(top=0.82, left=0.10, right=0.98, bottom=0.08)

    plt.show()

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) > 1:
        selected_scan = int(sys.argv[1])
    else:
        selected_scan = TARGET_SCAN

    plot_single_scan(selected_scan)
