import gpiod
import time

# Pin configuration
LED_PIN = 18  # Change this to the GPIO pin your LED is connected to
CHIP_NAME = "gpiochip0"  # Default GPIO chip name

# Initialize GPIO chip and line
chip = gpiod.Chip(CHIP_NAME)
line = chip.get_line(LED_PIN)
line.request(consumer="led_blink", type=gpiod.LINE_REQ_DIR_OUT)

try:
    while True:
        line.set_value(1)  # Turn LED on
        time.sleep(1)  # Wait 1 second
        line.set_value(0)  # Turn LED off
        time.sleep(1)  # Wait 1 second
except KeyboardInterrupt:
    print("\nExiting and releasing GPIO...")
    line.release()  # Release the GPIO line

