"""
2025 SignWave
"""
import spidev
import RPi.GPIO as GPIO
import time

__SPI_BUS_SPEED__ = 3_600_000 #Hz (3.6 MHz) constrained by ADC

class SPIUninitializedError(Exception):
    pass

class SPI_DEVICE:

    def __init__(self, DEVICE_CS_PIN, SPI_BUS=0, SPI_MODE=0b00) -> None:
        """Constructor for an SPI device

        Parameters
        ----------
        DEVICE_CS_PIN : Int
            The GPIO that the device's CS_B pin is connected to.
        SPI_BUS : [TODO:parameter]
            [TODO:description]
        SPI_MODE : [TODO:parameter]
            [TODO:description]

        """
        self.CS_PIN = DEVICE_CS_PIN
        self.SPI_BUS=0
        self.SPI_MODE = SPI_MODE
        self.intialized = False
        self.spi = None

    def initialize_spi(self):
        """[TODO:description]"""
        if self.intialized:
            return
        #GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.CS_PIN, GPIO.OUT) # Program GPIO to CS_B
        GPIO.output(self.CS_PIN, GPIO.HIGH) # Set the GPIO pin to High
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(self.SPI_BUS, 0)
        self.spi.max_speed_hz = __SPI_BUS_SPEED__
        self.spi.mode = self.SPI_MODE
        self.intialized = True


    def read_regiser(self, register_addr):
        """[TODO:description]

        Parameters
        ----------
        register_addr : Hexadecimal
            Address of the desired register in hexadecimal
        """
        if not self.intialized:
            raise SPIUninitializedError("SPI must be initalized before usage\nCall initalize_spi() before reading!")
        # Pull GPIO down to start read operation
        GPIO.output(self.CS_PIN, GPIO.LOW)
        #time.sleep(100e-9)

        address = register_addr | 0x80 # set MSB to 1 (read operation)
        dummy_byte = 0x00
        response = self.spi.xfer2([address, dummy_byte])

        # Release Slave (Pull it high)
        GPIO.output(self.CS_PIN, GPIO.HIGH)

        return response

    def write_register(self, register_addr, value):
        GPIO.output(self.CS_PIN, GPIO.LOW)  # Select IMU (CS LOW)
        #time.sleep(0.001)  # Short delay

        address = register_addr & 0x7F
        self.spi.xfer2([address, value])  # Send address & data

        GPIO.output(self.CS_PIN, GPIO.HIGH)  # Deselect IMU (CS HIGH)

    def clean_up(self):
        GPIO.cleanup()
        self.spi.close()
