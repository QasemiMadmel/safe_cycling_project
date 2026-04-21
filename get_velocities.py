# get_velocities.py

import configurations as config
import numpy as np
import os
from save_measurement import save_velocities_radial
from save_measurement import save_values_x_y

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

filepath_radial = os.path.join(measurement_dir, "radial_velocities.csv")
filepath_xy = os.path.join(measurement_dir, "velocities_x_y.csv")

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
