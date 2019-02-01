import RPi.GPIO as GPIO
import time

led = 18
GPIO.setmode(GPIO.BCM)

GPIO.setup(led, GPIO.OUT)
p = GPIO.PWM(led, 50)
p.start(7.5)

try:
    while True:
        p.ChangeDutyCycle(7.5)
        time.sleep(1)
        p.ChangeDutyCycle(12.5)
        time.sleep(1)
        p.ChangeDutyCycle(2.5)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

