#!/opt/miniconda3/bin/python
import RPi.GPIO as gpio
import time

trig, echo = 27, 17
gpio.setmode(gpio.BCM)

gpio.setwarnings(False)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)


def ping_cm():
    end, start = None, None
    try:
        gpio.output(trig, True)
        time.sleep(0.0001)
        gpio.output(trig, False)

        while not gpio.input(echo):
            start = time.time()
            if time.time() - start > 3:
                break

        while gpio.input(echo):
            end = time.time()
        if end is not None:
            sig_time = end - start
            distance = sig_time / 0.000058
            time.sleep(0.1)
            return int(distance)
    except (KeyboardInterrupt, RuntimeError):
        gpio.cleanup()


if __name__ == '__main__':
    while True:
        print(ping_cm())
