# get_velocities.py

import configurations as config
import numpy as np
import os
from save_measurement import save_vx_vy
from filename_handler import create_filename, get_common_suffix

# filepath to store computed results in measurement directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath_v_xy = create_filename(BASE_DIR, "velocities_x_y", config.suffix)
    
def get_x_y_velocities(xPrevious, xCurrent, yPrevious, yCurrent, timeInBetweenScans, t):
    
    # calculate x and y velocity between two scans     
    velocityX = (xCurrent - xPrevious) / timeInBetweenScans
    velocityY = (yCurrent - yPrevious) / timeInBetweenScans
    
    # calculate absolute value of velocity vectors
    velocity = np.sqrt(velocityX**2 + velocityY**2)
    
    # keep only proper velocioty values (up to 60 km/h)
    velocity[(velocity > 17) | (velocity < 0.1)] = np.nan 
        
    # save all information in a csv ofile for later
    save_vx_vy(filepath_v_xy, t, velocityX, velocityY, velocity)
    
    # return the results
    return velocityX, velocityY, velocity
