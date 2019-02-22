#!/opt/miniconda3/bin/python
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

trig = 4
echo = 18

gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)

gpio.output(trig, True)
time.sleep(1)
gpio.output(trig, False)
end, start = None, None

while not gpio.input(echo):
    start = time.time()

while gpio.input(echo):
    end = time.time()

sig_time = end - start
distance = sig_time / 0.000058
print('Detected distance: {}cm'.format(round(distance, 2)))

gpio.cleanup()

