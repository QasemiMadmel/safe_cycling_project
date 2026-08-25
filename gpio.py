from gpiozero import DigitalOutputDevice
from signal import pause

GPIO_PIN = 17  # BCM 17 = physischer Pin 11

output = DigitalOutputDevice(
    GPIO_PIN,
    active_high=True,
    initial_value=True
)

output.on()

print("GPIO 17 ist HIGH. Mit Ctrl+C beenden.")

try:
    pause()
except KeyboardInterrupt:
    output.off()
    output.close()
    print("GPIO 17 ist wieder LOW.")from gpiozero import DigitalOutputDevice
from signal import pause

GPIO_PIN = 17  # BCM 17 = physischer Pin 11

output = DigitalOutputDevice(
    GPIO_PIN,
    active_high=True,
    initial_value=True
)

output.on()

print("GPIO 17 ist HIGH. Mit Ctrl+C beenden.")

try:
    pause()
except KeyboardInterrupt:
    output.off()
    output.close()
    print("GPIO 17 ist wieder LOW.")
