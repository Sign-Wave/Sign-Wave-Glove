#!/usr/bin/env python3
import spidev
import time
import sys

# Configuration
SPI_BUS = 0      # SPI0 on Raspberry Pi
SPI_DEV = 0      # CE0 -> MCP3008 CS
SPI_MAX_HZ = 1000000  # 1 MHz is safe for 3.3V operation
VREF = 3.3       # Using Pi 3.3V for MCP3008 VREF
CHANNEL = 0      # We only read CH0
PRINT_HZ = 20    # How many lines per second to print

def open_spi(bus=SPI_BUS, dev=SPI_DEV, max_hz=SPI_MAX_HZ):
    spi = spidev.SpiDev()
    spi.open(bus, dev)
    spi.max_speed_hz = max_hz
    spi.mode = 0b00   # MCP3008 requires SPI mode 0
    spi.bits_per_word = 8
    return spi

def read_mcp3008_single(spi, ch):
    """
    Read a single-ended channel (0..7) from MCP3008.
    Returns an integer 0..1023 (10-bit).
    Protocol (3 bytes):
      1) Start bit = 1
      2) SGL/DIFF=1 (single-ended), D2..D0 = channel
      3) dummy
    """
    if not (0 <= ch <= 7):
        raise ValueError("Channel must be 0..7")

    # Build command: [00000001] [1ccc0000] [00000000]
    cmd1 = 0x01
    cmd2 = 0x80 | (ch << 4)  # 0b1000_0000 | (ch << 4)
    resp = spi.xfer2([cmd1, cmd2, 0x00])

    # resp[1] lower 2 bits and resp[2] form the 10-bit result
    value = ((resp[1] & 0x03) << 8) | resp[2]
    return value

def main():
    try:
        spi = open_spi()
    except FileNotFoundError:
        print("ERROR: /dev/spidev0.0 not found. Enable SPI and reboot.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading MCP3008 CH{CHANNEL} on SPI{SPI_BUS}.{SPI_DEV} @ {SPI_MAX_HZ/1_000_000:.1f} MHz (Vref={VREF} V)")
    period = 1.0 / PRINT_HZ
    try:
        next_t = time.perf_counter()
        while True:
            raw = read_mcp3008_single(spi, CHANNEL)
            volts = (raw / 1023.0) * VREF
            print(f"{raw:4d}  |  {volts:0.4f} V")
            next_t += period
            # simple pacing to avoid spamming the terminal
            sleep_for = next_t - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                next_t = time.perf_counter()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        spi.close()

if __name__ == "__main__":
    main()

