from spi_funcs import SPI_DEVICE
import time

# SPI Configuration
SPI_BUS = 0  # Typically 0 for Raspberry Pi, adjust for other platforms
BMI323_CS = 8  # Set to the correct SPI device (CS line)
CHIP_ID_REG = 0x00  # Register address for CHIP_ID


def main():
    bmi323 = SPI_DEVICE(BMI323_CS, SPI_BUS=SPI_BUS, SPI_SPEED=1_000_000)
    bmi323.initialize_spi()
    time.sleep(0.1)
    response = bmi323.read_register(CHIP_ID_REG)
    chip_id = response[1]

    print(f"CHIP_ID: 0x{chip_id:02X}")

    bmi323.clean_up()

if __name__ == "__main__":
    main()

