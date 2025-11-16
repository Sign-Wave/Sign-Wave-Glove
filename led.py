import lgpio as gpio
import time
import threading


class led:
    def __init__(self, gpio_pin, active_high = 1, default = 0, is_input = 0) -> None:
        self.gpio_pin = gpio_pin
        self.gpio_chip = None
        self.active_high = active_high
        self.default = default
        self.is_input = is_input
        
        
        self.__gpio_init(self.default)

    
    def __gpio_init(self, default):
        """
        Initialize GPIO using `lgpio`.
        """
        self.gpio_chip = gpio.gpiochip_open(0)
        if not self.is_input:
            gpio.gpio_claim_output(self.gpio_chip, self.gpio_pin)
            gpio.gpio_write(self.gpio_chip, self.gpio_pin, default)
        else:
            gpio.gpio_claim_input(self.gpio_chip, self.gpio_pin, gpio.SET_PULL_DOWN)

    
    def turn_on(self, duration=-1.0):
        if self.is_input:
            return
        gpio.gpio_write(self.gpio_chip, self.gpio_pin, 1 if self.active_high else 0)
        if duration != -1:
            threading.Thread(target=self.__turn_off_auto, args=[duration], daemon=True).start()

    def __turn_off_auto(self, duration):
         time.sleep(duration)
         self.turn_off()
    
    def read_value(self):
        return gpio.gpio_read(self.gpio_chip, self.gpio_pin)

    def turn_off(self):
        if self.is_input:
            return
        gpio.gpio_write(self.gpio_chip, self.gpio_pin, 0 if self.active_high else 1)

    def cleanup(self):
        gpio.gpiochip_close(self.gpio_chip)
