import spidev
import time

# SPI Configuration
SPI_BUS = 0  # Typically 0 for Raspberry Pi, adjust for other platforms
BMI323_CS = 0  # Set to the correct SPI device (CS line)
CHIP_ID_REG = 0x00  # Register address for CHIP_ID

def initialize_spi():
    spi = spidev.SpiDev()  # Create an SPI object
    spi.open(SPI_BUS, BMI323_CS)  # Open SPI bus
    spi.max_speed_hz = 1000000  # Set SPI clock speed (1 MHz to start)
    spi.mode = 0b00  # Use SPI Mode 0 (CPOL=0, CPHA=0) or Mode 3 (CPOL=1, CPHA=1)
    
    return spi

def read_chip_id(spi):
    """ Reads the CHIP_ID register """
    reg_address = CHIP_ID_REG | 0x80  # Set MSB to 1 for SPI read operation
    response = spi.xfer2([reg_address, 0x00])  # Send address, read response
    return response[1]  # The second byte is the actual CHIP_ID

def main():
    spi = initialize_spi()
    time.sleep(0.1)  # Allow some time for the IMU to power up

    chip_id = read_chip_id(spi)
    print(f"CHIP_ID: 0x{chip_id:02X}")

    spi.close()  # Close the SPI connection

if __name__ == "__main__":
    main()

