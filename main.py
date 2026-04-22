import signal
import sys
import numpy as np
import matplotlib.pyplot as plt
import configurations as config
from data_acquisition import LidarReader
from get_velocities import getVelocitiesRadial
from get_velocities import getXandYVelocities

running = True

def stop_handler(signum, frame):
    global running
    print(f"Stop signal received: {signum}")
    running = False

def main():
    global running

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    lidar = None

    try:
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

        while running:
            r, x, y, timestamp = lidar.getScan()

            currentScan = r
            currentX = x
            currentY = y
            dt = timestamp - previousTimestamp

            # getVelocitiesRadial(previousScan, currentScan, dt)
            getXandYVelocities(
                previousValuesX,
                currentX,
                previousValuesY,
                currentY,
                dt,
                timestamp
            )

            sc.set_offsets(np.column_stack((x, y)))
            plt.pause(0.001)

            previousScan = currentScan.copy()
            previousValuesX = currentX.copy()
            previousValuesY = currentY.copy()
            previousTimestamp = timestamp

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping...")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Cleaning up and exiting...")

        if lidar is not None:
            if hasattr(lidar, "stop"):
                try:
                    lidar.stop()
                except Exception as e:
                    print(f"Error in lidar.stop(): {e}")

            if hasattr(lidar, "disconnect"):
                try:
                    lidar.disconnect()
                except Exception as e:
                    print(f"Error in lidar.disconnect(): {e}")

            if hasattr(lidar, "close"):
                try:
                    lidar.close()
                except Exception as e:
                    print(f"Error in lidar.close(): {e}")

        plt.close('all')
        sys.exit(0)

if __name__ == "__main__":
    main()
