# plot_scenario.py

import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_dangerous_events(filename):
    
    tailgating_scans = []
    overtaking_scans = []

    filepath = Path(filename)

    if not filepath.exists():
        raise FileNotFoundError(
            f"The file does not exist: {filepath}"
        )

    with filepath.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row_number, row in enumerate(reader, start=1):

            # Ignore empty rows
            if not row:
                continue

            if len(row) < 2:
                print(
                    f"Row {row_number} is incomplete and was ignored: {row}"
                )
                continue

            try:
                scan_number = int(row[0])
            except ValueError:
                # This also allows a possible header row
                print(
                    f"Row {row_number} contains no valid scan number "
                    f"and was ignored: {row}"
                )
                continue

            scenario = row[1].strip().lower()

            if scenario == "tailgating":
                tailgating_scans.append(scan_number)

            elif scenario == "overtaking":
                overtaking_scans.append(scan_number)

            else:
                print(
                    f"Unknown scenario in row {row_number}: {scenario}"
                )

    return tailgating_scans, overtaking_scans


def plot_dangerous_events(filename):

    tailgating_scans, overtaking_scans = (
        load_dangerous_events(filename)
    )

    all_dangerous_scans = (
        tailgating_scans + overtaking_scans
    )

    if not all_dangerous_scans:
        print("No dangerous events were found.")
        return

    # Fixed vertical positions for the two scenarios
    tailgating_y = [1] * len(tailgating_scans)
    overtaking_y = [2] * len(overtaking_scans)

    figure, axis = plt.subplots(figsize=(14, 5))

    axis.scatter(
        tailgating_scans,
        tailgating_y,
        marker="x",
        s=80,
        linewidths=2,
        color="deeppink",
        label="Tailgating"
    )

    axis.scatter(
        overtaking_scans,
        overtaking_y,
        marker="x",
        s=80,
        linewidths=2,
        color="lightskyblue",
        label="Overtaking"
    )

    # Display the complete scan range
    first_scan = min(all_dangerous_scans)
    last_scan = max(all_dangerous_scans)

    axis.set_xlim(first_scan - 1, last_scan + 1)
    axis.set_ylim(0.5, 2.5)

    axis.set_yticks([1, 2])
    axis.set_yticklabels([
        "Tailgating",
        "Overtaking"
    ])

    axis.set_xlabel("Scan number")
    axis.set_ylabel("Detected scenario")
    axis.set_title("Detected dangerous events")

    axis.grid(
        True,
        axis="x",
        linestyle="--",
        alpha=0.5
    )

    axis.legend()

    figure.tight_layout()
    plt.show()


if __name__ == "__main__":

    filename = "/home/strawberry/safe_cycling_project/measurements/30082026_danger_detected_recording_233639.csv"
    plot_dangerous_events(filename)
