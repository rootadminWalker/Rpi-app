import RPi.GPIO as GPIO
import time

led = 4
GPIO.setmode(GPIO.BCM)

GPIO.setup(led, GPIO.OUT)

i = 0
while i <= 5:
    GPIO.output(led, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(led, GPIO.LOW)
    i += 1
GPIO.cleanup()

