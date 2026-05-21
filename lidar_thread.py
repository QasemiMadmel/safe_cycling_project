# lidar_thread.py

import threading

from data_acquisition import LidarReader


class LidarThread(threading.Thread):

    def __init__(self):

        # initialize thread
        super().__init__(daemon=True)

        # initialize lidar object
        self.lidar = LidarReader()

        # variable to stop thread safely
        self.running = True

        # latest scan storage
        self.latest_scan = None

    def run(self):

        while self.running:

            try:

                # get one complete scan
                r, x, y, t_log, timestamp, rssi = self.lidar.getScan()

                # store latest scan
                self.latest_scan = {
                    "r": r,
                    "x": x,
                    "y": y,
                    "t_log": t_log,
                    "timestamp": timestamp,
                    "rssi": rssi
                }

            except Exception as e:

                print(f"LidarThread Error: {e}")

    def stop(self):

        self.running = False
