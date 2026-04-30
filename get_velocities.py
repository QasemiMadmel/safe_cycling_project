# get_velocities.py

import configurations as config
import numpy as np
import os
from save_measurement import save_vx_vy_theta
from filename_handler import create_filename, get_common_suffix

# filepath to store computed results in measurement directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_v_xy = create_filename(BASE_DIR, "velocities_x_y", config.suffix)
    
def getXandYVelocities(xPrevious, xCurrent, yPrevious, yCurrent, timeInBetweenScans, t):
    
    # calculate x and y velocity between two scans     
    velocityX = (xCurrent - xPrevious) / timeInBetweenScans
    velocityY = (yCurrent - yPrevious) / timeInBetweenScans
    
    # calculate the angle of the velocity vector
    theta = getTheta(velocityX, velocityY)
    
    # save all information in a csv file for later
    save_vx_vy_theta(filepath_v_xy, velocityX, velocityY, t, theta)
    
    # return the results
    return velocityX, velocityY, theta

def getTheta(vx, vy):
    
    # arctan(vy,vx) to correctly handle signs and quadrant
    theta = np.degrees(np.atan2(vy,vx))
    
    # turn into range (0 - 360 degree) for a convenient interpretation
    theta_in_360 = (theta+360)%(360)
    
    # return the resulting angle in degree
    return theta_in_360
