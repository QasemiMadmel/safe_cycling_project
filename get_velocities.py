# get_velocities.py

import configurations as config
import numpy as np
import os
from save_measurement import save_velocities_radial
from save_measurement import save_values_x_y
from filename_handler import create_filename, get_common_suffix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

filepath_radial = create_filename(BASE_DIR, "radial_velocities.csv", config.suffix)
filepath_xy = create_filename(BASE_DIR, "velocities_x_y.csv", config.suffix)

def getVelocitiesRadial(previous, current, timeInBetweenScans):
    
    velocity = []
    if timeInBetweenScans == 0:
        print("time between scans is zero, skipping")
        return 
    else:
        velocity = (current - previous) / timeInBetweenScans
        save_velocities_radial(filepath_radial, velocity)
    
    return 
    
def getXandYVelocities(xPrevious, xCurrent, yPrevious, yCurrent, timeInBetweenScans, t):

    if timeInBetweenScans == 0:
        print("time between scans is zero, skipping")
        return 
    else:
        velocityX = (xCurrent - xPrevious) / timeInBetweenScans
        velocityY = (yCurrent - yPrevious) / timeInBetweenScans
    
    save_values_x_y(filepath_xy, velocityX, velocityY, t)
    
    return 
