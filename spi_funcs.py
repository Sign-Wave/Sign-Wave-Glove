"""
2025 SignWave
"""
import spidev
import lgpio as gpio
import time

__SPI_BUS_SPEED__ = 1 #3_600_000 #Hz (3.6 MHz) constrained by ADC


class SPI_DEVICE:

    def __init__(self, DEVICE_CS_PIN : int, SPI_BUS=0, SPI_DEVICE=0, SPI_MODE=0b00, SPI_SPEED=__SPI_BUS_SPEED__) -> None:
        """Initialize the SPI device

        Parameters
        ----------
        DEVICE_CS_PIN : Integer
            GPIO pin used as chip select
        SPI_BUS : Integer (0 or 1)
            SPI bus number
        SPI_DEVICE : Integer (0 or 1)
            SPI device
        SPI_MODE : Binary Number (0b00, 0b01, 0b10, 0b11)
            Determines the clocking behaviour
                CPOL (MSB)
                    Clock polarity
                CPHA (LSB)
                    Clock phase
            0b00 : Data sampled on rising edge and shifted out on the falling edge
            0b01 : Data sampled on the falling edge and shifted out on the rising edge
            0b10 : Data sampled on the falling edge and shifted out on the rising edge
            0b11 : Data sampled on the rising edge and shifted out on the falling edge
        SPI_SPEED : Hz
            Clocking speed of the serial interface.
            Frequency of SCLK
        """
        self.cs = DEVICE_CS_PIN
        self.spi_bus = SPI_BUS
        self.spi_device = SPI_DEVICE
        self.interface_freq = SPI_SPEED
        self.mode = SPI_MODE

        self.spi = None
        self.gpio_chip = None

        self.__initialize_gpio()
        self.__initialize_spi()


    def __initialize_spi(self):
        """[TODO:description]"""
        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_bus, self.spi_device)
        self.spi.mode = self.mode
        self.spi.max_speed_hz = self.interface_freq
        self.spi.lsbfirst = False # MSB-first transmission
        self.spi.cshigh = False # Active low CS

    def __initialize_gpio(self):
        """
        Initialize GPIO using `lgpio`.
        """
        self.gpio_chip = gpio.gpiochip_open(0)
        gpio.gpio_claim_output(self.gpio_chip, self.cs) # set CS pin as output
        gpio.gpio_write(self.gpio_chip, self.cs, 1) # Ensure CS is high

    def read_register(self, register_addr):
        """[TODO:description]

        Parameters
        ----------
        register_addr : Hexadecimal
            Address of the desired register in hexadecimal
        """
        # Pull GPIO down to start read operation
        gpio.gpio_write(self.gpio_chip, self.cs, 0) # Activate CS (LOW)
        time.sleep(1e-3)

        address = register_addr | 0x80 # set MSB to 1 (read operation)
        dummy_byte = 0x00
        response = self.spi.xfer2([address, dummy_byte])

        # Release Slave (Pull it high)
        time.sleep(1e-3)
        gpio.gpio_write(self.gpio_chip, self.cs, 1) # Deactivate CS (HIGH)

        return response

    def write_register(self, register_addr, value):
        gpio.gpio_write(self.gpio_chip, self.cs, 0) # Activate CS (LOW)
        time.sleep(1e-3)

        address = register_addr & 0x7F
        self.spi.xfer2([address, value])  # Send address & data

        time.sleep(1e-3)
        gpio.gpio_write(self.gpio_chip, self.cs, 1) # Deactivate CS (HIGH)

    def close(self):
        if self.spi:
            self.spi.close()
        if self.gpio_chip:
            gpio.gpiochip_close(self.gpio_chip)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
