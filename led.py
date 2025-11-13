import lgpio as gpio
import time
import threading


class led:
    def __init__(self, gpio_pin) -> None:
        self.gpio_pin = gpio_pin
        self.gpio_chip = None
        
        self.__gpio_init()

    
    def __gpio_init(self):
        """
        Initialize GPIO using `lgpio`.
        """
        self.gpio_chip = gpio.gpiochip_open(0)
        gpio.gpio_claim_output(self.gpio_chip, self.gpio_pin)
        gpio.gpio_write(self.gpio_chip, self.gpio_pin, 1)

    
    def turn_on(self, duration=-1.0):
        gpio.gpio_write(self.gpio_chip, self.gpio_pin, 0)
        if duration != -1:
            threading.Thread(target=self.__turn_off_auto, args=[duration], daemon=True).start()

    def __turn_off_auto(self, duration):
         time.sleep(duration)
         self.turn_off()

    def turn_off(self):
        gpio.gpio_write(self.gpio_chip, self.gpio_pin, 1)

    def cleanup(self):
        gpio.gpiochip_close(self.gpio_chip)
