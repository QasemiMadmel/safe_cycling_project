# get_velocities.py

import configurations as config
import numpy as np

def getVelocities(previous, current, timeInBetweenScans):
    
    velocity = []
    if timeInBetweenScans == 0:
        print("time between scans is zero, skipping")
        return resultIndices
    else:
        velocity = (current - previous) / timeInBetweenScans

    print("dt:", timeInBetweenScans)
    print("velocity sample:", velocity[:10])  # nur erste 10 Werte!
    print("min:", np.min(velocity), "max:", np.max(velocity))
    print("---------------------------")
    
    return velocity
