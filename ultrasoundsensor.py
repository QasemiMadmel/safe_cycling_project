# ultrasoundsensor.py

import RPi.GPIO as GPIO
import time

# configurations
US_SENSOR_TRIGGER = 23  # pin 16 
US_SENSOR_ECHO = 24     # pin 18
Messung_Max = 1               # s
Messung_Trigger = 0.00001     # s
Messung_Pause = 0.2           # 5 Hz
Messung_Faktor = (343460 / 2) # sound velocity in mm/s

Abstand_Max = 4000        # Max value in mm
Abstand_Max_Error = Abstand_Max + 1

def US_SENSOR_GetDistance():
    # triggering pin for 10 us
    GPIO.output(US_SENSOR_TRIGGER, True)
    time.sleep(Messung_Trigger)
    GPIO.output(US_SENSOR_TRIGGER, False)
 
    # save starting time
    StartZeit = time.time()
    MaxZeit = StartZeit + Messung_Max
    # waite for the echo
    while StartZeit < MaxZeit and GPIO.input(US_SENSOR_ECHO) == 0:
        StartZeit = time.time()
    
    # save the stop time
    StopZeit = StartZeit
    # waite for echo = 0
    while StopZeit < MaxZeit and GPIO.input(US_SENSOR_ECHO) == 1:
        StopZeit = time.time()
    if StopZeit < MaxZeit:
        # compute dt
        Zeit = StopZeit - StartZeit
        # compute distance
        Distanz = Zeit * Messung_Faktor
    else:
        # set distance to error value
        Distanz = Abstand_Max_Error
        
    # return distance value
    return int(Distanz)
 
if __name__ == '__main__':
    
    GPIO.setmode(GPIO.BCM)                    # GPIO Modus (BOARD / BCM)
    GPIO.setup(US_SENSOR_TRIGGER, GPIO.OUT)   # Trigger-Pin = Raspberry Pi Output
    GPIO.setup(US_SENSOR_ECHO, GPIO.IN)       # Echo-Pin = raspberry Pi Input
    try:
        while True:
            Abstand = US_SENSOR_GetDistance()
            
            if Abstand >= Abstand_Max:
                Abstand = -1
            else:
                # Ausgabe Text
                print(Abstand)
            
            time.sleep(Messung_Pause)
 
    # Beim Abbruch durch STRG+C: GPIO Port freigeben
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        GPIO.cleanup()
