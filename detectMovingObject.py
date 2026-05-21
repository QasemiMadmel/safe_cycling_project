# detectMovingObject.py

import numpy as np

def detectDanger(v, r, rssi, ego_velocity):

    danger_indices = []

    velocity_margin = 0.5
    max_distance = 5.0
    min_rssi = 0

    for idx in range(0, 212):

        if np.isnan(v[idx]):
            continue

        if v[idx] > ego_velocity + velocity_margin:
            if r[idx] < max_distance:
                if rssi[idx] >= min_rssi:
                    danger_indices.append(idx)

    return danger_indices


def detectTailgating(distances, ego_velocity):

    min_distance = 2.0

    if ego_velocity < 10/3.6:
        return False

    valid_count = 0

    for d in distances:

        if d is None:
            continue

        if d < min_distance:
            valid_count += 1

    return valid_count >= 4
