import threading
import time
import csv
import os

from ultrasoundsensor import UltrasoundReader


class UltrasoundThread(threading.Thread):

    def __init__(self, filepath):

        super().__init__(daemon=True)

        self.sensor = UltrasoundReader()
        self.filepath = filepath

        self.running = True

        self.latest_distance = None
        self.latest_timestamp = None

    def save_distance(self, timestamp, distance):

        file_exists = os.path.isfile(self.filepath)

        with open(self.filepath, "a", newline="") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["timestamp", "distance_m"])

            writer.writerow([timestamp, distance])

    def run(self):

        while self.running:

            distance = self.sensor.getDistance()

            timestamp = time.time()

            if distance is not None:

                self.latest_distance = distance
                self.latest_timestamp = timestamp

                self.save_distance(timestamp, distance)

                print(f"[US] {distance:.2f} m")

            time.sleep(0.05)

    def stop(self):

        self.running = False