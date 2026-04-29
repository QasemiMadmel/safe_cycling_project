# plot_velocity

import numpy as np
import configurations as config

def classify_velocity_direction(theta, right_mask, front_mask, left_mask):
    
    # define the colors based on the area of plot
    colors = np.full(len(theta), "blue", dtype=object) # blue is default
    colors[right_mask] = "green"
    colors[front_mask] = "orange"
    colors[left_mask]  = "magenta"

    # the approach angle values are arbitary and must be adapted later on. 
    # These values suppose to mark points that are moving in direction of the sensor  
    approach_right = right_mask & (theta >= config.RIGHT_APPROACH_MIN) & (theta <= config.RIGHT_APPROACH_MAX)
    approach_front = front_mask & (theta >= config.FRONT_APPROACH_MIN) & (theta <= config.FRONT_APPROACH_MAX)
    approach_left  = left_mask  & (theta >= config.LEFT_APPROACH_MIN) & (theta <= config.LEFT_APPROACH_MAX)

    # show points with a velocity vector directing toward sensor in "red"
    colors[approach_right] = "red"
    colors[approach_front] = "red"
    colors[approach_left]  = "red"

    return colors


def classify_velocity_direction_playback(theta):
    
    # make an array instead of using the list
    theta = np.array(theta)
    # capture the length of the array
    n = len(theta)
    # create an array of colors with the default color blue
    colors = np.full(n, "blue", dtype=object)
    
    # use bool arrays to define areas around sensor: [False, False, False, ...]
    right_mask = np.zeros(n, dtype=bool)
    front_mask = np.zeros(n, dtype=bool)
    left_mask  = np.zeros(n, dtype=bool)

    right_mask[:n//3] = True              # set the first 1/3rd of the array to true
    front_mask[n//3:2*n//3] = True        # set the area from 1/3rd to 2/3rd of the array to true
    left_mask[2*n//3:] = True             # set the last 1/3rd to true

    # paint the areas with different colors
    colors[right_mask] = "green"
    colors[front_mask] = "orange"
    colors[left_mask]  = "magenta"

    # arbitary values that mark the points that are directing towards sensor 
    approach_right = right_mask & (theta >= config.RIGHT_APPROACH_MIN) & (theta <= config.RIGHT_APPROACH_MAX)
    approach_front = front_mask & (theta >= config.FRONT_APPROACH_MIN) & (theta <= config.FRONT_APPROACH_MAX)
    approach_left  = left_mask  & (theta >= config.LEFT_APPROACH_MIN) & (theta <= config.LEFT_APPROACH_MAX)

    # visualize distance values pointing to sensor in red
    colors[approach_right] = "red"
    colors[approach_front] = "red"
    colors[approach_left]  = "red"

    # return the resulted colors for visualization in plot
    return colors
