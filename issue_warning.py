# issue_warning.py

import time 
import threading 
from gpiozero import DigitalOutputDevice

WARNING_GPIO_PIN = 17 # pin 11
WARNING_DURATION = 1.0

def issue_warning(danger_event: threading.Event, 
				stop_event: threading.Event)-> None:
	
	# define the desired output (GPIO is set to high) 
	warning_output = DigitalOutputDevice(WARNING_GPIO_PIN, active_high=True, initial_value=False)
	
	try:
		while not stop_event.is_set():
			danger_event.wait()
			
			if stop_event.is_set():
				break
			danger_event.clear()
			warning_output.on()
			warning_until = time.monotonic() + WARNING_DURATION
			print("danger occured")
			
			while not stop_event.is_set():
				remaining_time = warning_until - time.monotonic() # keep track of the ending time
				
				if remaining_time <= 0:
					break
				
				new_danger= danger_event.wait(timeout=remaining_time) # danger occured in the waiting time (True/False)
				
				if new_danger:
					print("new_danger occured")
					danger_event.clear()
					warning_until = time.monotonic() + WARNING_DURATION # if danger extend the amount of warning time
			warning_output.off()
	finally:
		# stop_event received or no active warning -> end the warning_output
		print("danger_event stopped")
		warning_output.off()
		warning_output.close()
