from led import led

RED_PIN = 23
GREEN_PIN = 24

green_led = led(GREEN_PIN)
red_led = led(RED_PIN)

if __name__ == '__main__':
    print(__name__)
    for i in range(10):
        green_led.turn_on(1)
        red_led.turn_on(1)

    green_led.cleanup()
    red_led.cleanup()
