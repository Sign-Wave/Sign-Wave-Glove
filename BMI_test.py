from spi_funcs import SPI_DEVICE
import time

# SPI Configuration
SPI_BUS = 0  # Typically 0 for Raspberry Pi, adjust for other platforms
BMI323_CS = 8  # Set to the correct SPI device (CS line)
CHIP_ID_REG = 0x00  # Register address for CHIP_ID


def main():
    with SPI_DEVICE(DEVICE_CS_PIN=BMI323_CS, SPI_BUS=SPI_BUS) as spi:
        response = spi.read_register(register_addr=CHIP_ID_REG)
        print(response)
        #print(f"CHIP_ID: 0x{chip_id:02X}")


if __name__ == "__main__":
    main()

