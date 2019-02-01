import RPi.GPIO as GPIO
import time

led = 18
GPIO.setmode(GPIO.BCM)

GPIO.setup(led, GPIO.OUT)

try:
    while True:
        GPIO.output(led, 1)
        time.sleep(0.0015)
        GPIO.output(led, 0)
except KeyboardInterrupt:
    GPIO.cleanup()

