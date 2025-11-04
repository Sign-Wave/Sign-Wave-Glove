#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus2
import spidev
import time
import math
import sys

# ---------------------------
# Config
# ---------------------------
SPI_BUS = 0
SPI_DEV = 0
SPI_MAX_HZ = 1_000_000
FLEX_CHANNELS = [0, 1, 2, 3, 4]  # connected flex sensors

# I2C / MPU-6050
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
ACCEL_SF = 16384.0
GYRO_SF  = 131.0

PRINT_HZ = 10
CALIBRATION_TIME = 1.0

# ---------------------------
# MCP3008 helpers
# ---------------------------
def open_spi():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEV)
    spi.max_speed_hz = SPI_MAX_HZ
    spi.mode = 0b00
    return spi

def read_mcp3008_single(spi, ch):
    cmd1 = 0x01
    cmd2 = 0x80 | (ch << 4)
    resp = spi.xfer2([cmd1, cmd2, 0x00])
    return ((resp[1] & 0x03) << 8) | resp[2]

# ---------------------------
# MPU-6050 helpers
# ---------------------------
def read_word(bus, reg):
    hi = bus.read_byte_data(MPU6050_ADDR, reg)
    lo = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    val = (hi << 8) | lo
    if val > 32767:
        val -= 65536
    return val

def setup_mpu(bus):
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.05)

def accel_to_angles(ax_g, ay_g, az_g):
    roll  = math.degrees(math.atan2(ay_g, az_g if abs(az_g) > 1e-8 else 1e-8))
    pitch = math.degrees(math.atan2(-ax_g, math.sqrt(ay_g*ay_g + az_g*az_g)))
    return roll, pitch

def calibrate(bus):
    print("\nCalibrating... keep the hand steady")
    t_end = time.time() + CALIBRATION_TIME
    gx_sum = gy_sum = gz_sum = 0.0
    ax_sum = ay_sum = az_sum = 0.0
    n = 0
    while time.time() < t_end:
        ax = read_word(bus, ACCEL_XOUT_H) / ACCEL_SF
        ay = read_word(bus, ACCEL_XOUT_H + 2) / ACCEL_SF
        az = read_word(bus, ACCEL_XOUT_H + 4) / ACCEL_SF
        gx = read_word(bus, GYRO_XOUT_H) / GYRO_SF
        gy = read_word(bus, GYRO_XOUT_H + 2) / GYRO_SF
        gz = read_word(bus, GYRO_XOUT_H + 4) / GYRO_SF
        ax_sum += ax; ay_sum += ay; az_sum += az
        gx_sum += gx; gy_sum += gy; gz_sum += gz
        n += 1
        time.sleep(0.002)
    if n == 0: n = 1
    bx, by, bz = gx_sum/n, gy_sum/n, gz_sum/n
    ax0, ay0, az0 = ax_sum/n, ay_sum/n, az_sum/n
    r0, p0 = accel_to_angles(ax0, ay0, az0)
    print("Calibration done.\n")
    return (bx, by, bz), (r0, p0)

# ---------------------------
# Main
# ---------------------------
def main():
    try:
        spi = open_spi()
    except FileNotFoundError:
        print("ERROR: SPI not found. Enable it in raspi-config.", file=sys.stderr)
        sys.exit(1)

    bus = smbus2.SMBus(1)
    setup_mpu(bus)

    print("Hold glove steady, then press ENTER to calibrate IMU...")
    input()
    (bx, by, bz), (roll, pitch) = calibrate(bus)

    alpha = 0.98
    dt_target = 1.0 / PRINT_HZ
    t_prev = time.perf_counter()

    print("\n ROLL   PITCH  |  F0   F1   F2   F3   F4")
    print("-------------------------------------------")

    try:
        while True:
            # IMU
            ax = read_word(bus, ACCEL_XOUT_H) / ACCEL_SF
            ay = read_word(bus, ACCEL_XOUT_H + 2) / ACCEL_SF
            az = read_word(bus, ACCEL_XOUT_H + 4) / ACCEL_SF
            gx = read_word(bus, GYRO_XOUT_H) / GYRO_SF - bx
            gy = read_word(bus, GYRO_XOUT_H + 2) / GYRO_SF - by

            t_now = time.perf_counter()
            dt = t_now - t_prev
            if dt <= 0: dt = dt_target
            t_prev = t_now

            roll_g  = roll  + gx * dt
            pitch_g = pitch + gy * dt
            roll_acc, pitch_acc = accel_to_angles(ax, ay, az)
            roll  = alpha * roll_g  + (1.0 - alpha) * roll_acc
            pitch = alpha * pitch_g + (1.0 - alpha) * pitch_acc

            # Flex
            flex_vals = [read_mcp3008_single(spi, ch) for ch in FLEX_CHANNELS]

            # Print
            flex_strs = [f"{val:4d}" for val in flex_vals]
            print(" {:+6.2f}  {:+6.2f}  | ".format(roll, pitch) + "  ".join(flex_strs))

            # pacing
            sleep_for = dt_target - (time.perf_counter() - t_now)
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        spi.close()
        bus.close()

if __name__ == "__main__":
    main()
