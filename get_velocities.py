# get_velocities.py

import configurations as config
import numpy as np
import os
from save_measurement import save_vx_vy_theta
from filename_handler import create_filename, get_common_suffix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

filepath_v_xy = create_filename(BASE_DIR, "velocities_x_y.csv", config.suffix)
    
def getXandYVelocities(xPrevious, xCurrent, yPrevious, yCurrent, timeInBetweenScans, t):

    if timeInBetweenScans == 0:
        print("time between scans is zero, skipping")
        return None, None, None
    else:
        velocityX = (xCurrent - xPrevious) / timeInBetweenScans
        velocityY = (yCurrent - yPrevious) / timeInBetweenScans
        theta = getTheta(velocityX, velocityY)
    
    save_vx_vy_theta(filepath_v_xy, velocityX, velocityY, t, theta)
    
    return velocityX, velocityY, theta

def getTheta(vx, vy):
    theta = np.degrees(np.atan2(vy,vx))
    theta_in_360 = (theta+360)%(360)
    return theta_in_360
