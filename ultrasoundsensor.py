# ultrasoundsensor.py

import time
import RPi.GPIO as GPIO
import configurations as config


class UltrasoundReader:

    def __init__(self):

        self.last_distance = None
        self.last_measurement = 0
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(config.US_SENSOR_TRIGGER, GPIO.OUT)
        GPIO.setup(config.US_SENSOR_ECHO, GPIO.IN)

    def getDistance(self):

        now = time.time()
        
        if now - self.last_measurement < 0.2:
            return self.last_distance
        
        GPIO.output(config.US_SENSOR_TRIGGER, False)
        time.sleep(0.000002)

        GPIO.output(config.US_SENSOR_TRIGGER, True)
        time.sleep(config.US_TRIGGER_TIME)
        GPIO.output(config.US_SENSOR_TRIGGER, False)

        start_time = time.time()
        max_time = start_time + config.US_TIMEOUT

        while start_time < max_time and GPIO.input(config.US_SENSOR_ECHO) == 0:
            start_time = time.time()

        stop_time = start_time

        while stop_time < max_time and GPIO.input(config.US_SENSOR_ECHO) == 1:
            stop_time = time.time()

        if stop_time >= max_time:
            return self.last_distance

        dt = stop_time - start_time

        distance_mm = dt * config.US_SOUND_SPEED

        distance = distance_mm / 1000.0
        
        self.last_distance = distance
        self.last_measurement = now
        
        return distance
