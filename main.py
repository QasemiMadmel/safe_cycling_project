# main.py

import numpy as np
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from get_velocities import getVelocitiesRadial
from get_velocities import getXandYVelocities

def main():

    lidar = LidarReader()

    plt.ion()
    fig, ax = plt.subplots()
    sc = ax.scatter([], [], s=2)
    ax.set_aspect('equal')
    ax.set_xlim(-config.PLOT_X_LIMIT, config.PLOT_X_LIMIT)
    ax.set_ylim(-config.PLOT_Y_LIMIT, config.PLOT_Y_LIMIT)

    r, x, y, timestamp = lidar.getScan()
    previousScan = r.copy()
    previousValuesX = x.copy()
    previousValuesY = y.copy()
    previousTimestamp = timestamp

    while True:
        r, x, y, timestamp = lidar.getScan()

        currentScan = r
        currentX = x
        currentY = y
        dt = timestamp - previousTimestamp

        getVelocitiesRadial(previousScan, currentScan, dt)
        #getXandYVelocities(previousValuesX, currentX, previousValuesY, currentY, dt, timestamp)

        sc.set_offsets(np.column_stack((x, y)))
        plt.pause(0.001)
        previousScan = currentScan.copy()
        previousValuesX = currentX.copy()
        previousValuesY = currentY.copy()
        previousTimestamp = timestamp

if __name__ == "__main__":
    main()

