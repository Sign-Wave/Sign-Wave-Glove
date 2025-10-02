#!/usr/bin/env python3
import spidev
import time
import sys

# Configuration
SPI_BUS = 0           # SPI0 on Raspberry Pi
SPI_DEV = 0           # CE0 -> MCP3008 CS
SPI_MAX_HZ = 1_000_000  # 1 MHz is safe for 3.3V operation
VREF = 3.3            # Using Pi 3.3V for MCP3008 VREF
CHANNELS = [0, 1, 2, 3, 4]  # Read CH0..CH3 for the 4 flex sensors
PRINT_HZ = 20         # Lines per second

def open_spi(bus=SPI_BUS, dev=SPI_DEV, max_hz=SPI_MAX_HZ):
    spi = spidev.SpiDev()
    spi.open(bus, dev)
    spi.max_speed_hz = max_hz
    spi.mode = 0b00   # MCP3008 requires SPI mode 0
    spi.bits_per_word = 8
    return spi

def read_mcp3008_single(spi, ch: int) -> int:
    """
    Read a single-ended channel (0..7) from MCP3008.
    Returns an integer 0..1023 (10-bit).
    """
    if not (0 <= ch <= 7):
        raise ValueError("Channel must be 0..7")
    # Command: start bit + single-ended + channel
    cmd1 = 0x01
    cmd2 = 0x80 | (ch << 4)
    resp = spi.xfer2([cmd1, cmd2, 0x00])
    return ((resp[1] & 0x03) << 8) | resp[2]

def main():
    try:
        spi = open_spi()
    except FileNotFoundError:
        print("ERROR: /dev/spidev0.0 not found. Enable SPI and reboot.", file=sys.stderr)
        sys.exit(1)

    ch_list = ",".join(str(c) for c in CHANNELS)
    print(f"Reading MCP3008 CH[{ch_list}] on SPI{SPI_BUS}.{SPI_DEV} @ {SPI_MAX_HZ/1_000_000:.1f} MHz (Vref={VREF} V)")
    # Print a header once so columns are easy to read
    header_cols = [f"CH{ch} Raw  Volts" for ch in CHANNELS]
    print(" | ".join(f"{h:<14}" for h in header_cols))

    period = 1.0 / PRINT_HZ
    try:
        next_t = time.perf_counter()
        while True:
            parts = []
            for ch in CHANNELS:
                raw = read_mcp3008_single(spi, ch)
                volts = (raw / 1023.0) * VREF
                # Fixed-width columns for aligned output
                parts.append(f"{raw:4d}  {volts:0.4f}V")
            print(" | ".join(f"{p:<14}" for p in parts), flush=True)

            next_t += period
            # pacing to target PRINT_HZ
            sleep_for = next_t - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # if we fell behind, reset the schedule
                next_t = time.perf_counter()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        spi.close()

if __name__ == "__main__":
    main()
