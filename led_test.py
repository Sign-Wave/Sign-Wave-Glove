from led import led
import time

RED_PIN = 24
#GREEN_PIN = 24
#VIBRATE_PIN = 25

#green_led = led(GREEN_PIN)
red_led = led(RED_PIN)
#motor = led(VIBRATE_PIN)

if __name__ == '__main__':
    print(__name__)
    for i in range(10):
        #green_led.turn_on(1)
        red_led.turn_on(1)
        #motor.turn_on(1)
    red_led.turn_off()
    #green_led.turn_off()
    #motor.turn_off()    

    #green_led.cleanup()
    red_led.cleanup()
