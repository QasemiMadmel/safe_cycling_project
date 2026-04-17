# main.py

import numpy as np
import matplotlib.pyplot as plt 
import configurations as config 
from data_acquisition import LidarReader
from get_velocities import getVelocities

def main(): 
    lidar = LidarReader()
	
    # prepare plot
    plt.ion()
    fig, ax = plt.subplots()
    sc = ax.scatter([], [], s=2)
    #scMoves = ax.scatter([], [], s=10)

    ax.set_aspect('equal')
    ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
    ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)
    
    # capture the very first scan
    r, x, y, timestamp = lidar.getScan()
    previousScan = r.copy()
    previousTimestamp = timestamp

    while True:
	    r, x, y, timestamp = lidar.getScan()
	    
	    sc.set_offsets(list(zip(x, y)))
	    
	    currentScan = r
	    dt = timestamp - previousTimestamp
        
	    indicesOfMovingObject = getVelocities(previousScan, currentScan, dt)
	    
	    points = np.column_stack((x, y))
	    sc.set_offsets(points)
	    plt.pause(0.001)
	    
	    previousScan = currentScan.copy()
	    previousTimestamp = timestamp
 
if __name__ == "__main__":
    main()
		
