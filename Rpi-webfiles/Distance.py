#!/opt/miniconda3/bin/python
import RPi.GPIO as gpio
import time

trig, echo = 27, 17


def setup(trig_pin=27, echo_pin=17):
    global trig, echo
    trig = trig_pin
    echo = echo_pin
    gpio.setmode(gpio.BCM)

    gpio.setwarnings(False)
    gpio.setup(trig, gpio.OUT)
    gpio.setup(echo, gpio.IN)


def ping_cm():
    global trig, echo
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
    except RuntimeError:
        gpio.cleanup()
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    while True:
        dis = ping_cm()
        if dis != 0:
            print(dis)
        else:
            break
