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
        
        # locking the thread to avoid racing conditions
        self.lock = threading.Lock()
        

    def run(self):

        while self.running:

            try:

                # get one complete scan
                r, x, y, t_log, timestamp, scan_number = self.lidar.getScan()

                # store latest scan
                new_scan = {
                    "r": r,
                    "x": x,
                    "y": y,
                    "t_log": t_log,
                    "timestamp": timestamp,
                    "scan_number": scan_number
                }
                
                with self.lock:
                    self.latest_scan = new_scan

            except Exception as e:

                print(f"LidarThread Error: {e}")
                time.sleep(0.1)

    def stop(self):

        self.running = False
