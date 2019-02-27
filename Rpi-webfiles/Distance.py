#!/opt/miniconda3/bin/python
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

trig = 4
echo = 17

gpio.setwarnings(False)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)
end, start = None, None

try:
    while True:
        gpio.output(trig, True)
        time.sleep(0.0001)
        gpio.output(trig, False)

        start_while = time.time()
        while not gpio.input(echo):
            start = time.time()
            print(time.time() - start_while)
            if time.time() - start_while > 3:
                break

        while gpio.input(echo):
            end = time.time()
        if end is not None:
            sig_time = end - start
            distance = sig_time / 0.000058
            print('Detected distance: {}cm'.format(round(distance, 2)))
            time.sleep(1)
except KeyboardInterrupt:
    gpio.cleanup()
