# detect_moving_object.py

import numpy as np

def detect_danger(v, r, ego_velocity):

    danger_indices = []

    velocity_margin = 0.5
    max_distance = 5.0

    for idx in range(0, 212):

        if np.isnan(v[idx]):
            continue

        if v[idx] > ego_velocity + velocity_margin:
            if r[idx] < max_distance:
                    danger_indices.append(idx)

    return danger_indices


