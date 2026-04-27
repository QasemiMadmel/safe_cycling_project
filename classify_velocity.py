# plot_velocity

import numpy as np
import configurations as config

def classify_velocity_direction(theta, right_mask, front_mask, left_mask):
    
    colors = np.full(len(theta), "blue", dtype=object)

    colors[right_mask] = "green"
    colors[front_mask] = "orange"
    colors[left_mask]  = "magenta"

    approach_right = right_mask & (theta >= config.RIGHT_APPROACH_MIN) & (theta <= config.RIGHT_APPROACH_MAX)
    approach_front = front_mask & (theta >= config.FRONT_APPROACH_MIN) & (theta <= config.FRONT_APPROACH_MAX)
    approach_left  = left_mask  & (theta >= config.LEFT_APPROACH_MIN) & (theta <= config.LEFT_APPROACH_MAX)

    colors[approach_right] = "red"
    colors[approach_front] = "red"
    colors[approach_left]  = "red"

    return colors


def classify_velocity_direction_playback(theta):

    theta = np.array(theta)
    n = len(theta)

    colors = np.full(n, "blue", dtype=object)

    right_mask = np.zeros(n, dtype=bool)
    front_mask = np.zeros(n, dtype=bool)
    left_mask  = np.zeros(n, dtype=bool)

    right_mask[:n//3] = True
    front_mask[n//3:2*n//3] = True
    left_mask[2*n//3:] = True

    colors[right_mask] = "green"
    colors[front_mask] = "orange"
    colors[left_mask]  = "magenta"

    approach_right = right_mask & (theta >= config.RIGHT_APPROACH_MIN) & (theta <= config.RIGHT_APPROACH_MAX)
    approach_front = front_mask & (theta >= config.FRONT_APPROACH_MIN) & (theta <= config.FRONT_APPROACH_MAX)
    approach_left  = left_mask  & (theta >= config.LEFT_APPROACH_MIN) & (theta <= config.LEFT_APPROACH_MAX)

    colors[approach_right] = "red"
    colors[approach_front] = "red"
    colors[approach_left]  = "red"

    return colors
