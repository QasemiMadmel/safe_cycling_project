# get_velocities.py

import configurations as config
import numpy as np
from save_measurement import save_velocities

def getVelocities(previous, current, timeInBetweenScans):
    
    velocity = []
    if timeInBetweenScans == 0:
        print("time between scans is zero, skipping")
        return resultIndices
    else:
        velocity = (current - previous) / timeInBetweenScans
        save_velocities("velocities.csv", velocity)
    
    print("dt:", timeInBetweenScans)
    print("velocity sample:", velocity[500:530])  # 30 values in front area of the sensor
    print("min:", np.min(velocity), "max:", np.max(velocity)) # max and min values in one scan 
    print("---------------------------")
    
    return velocity
