#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus2
import time
import math
import sys

# I2C address and MPU-6050 registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
ACCEL_CONFIG = 0x1C
GYRO_CONFIG  = 0x1B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A

# Scale factors for default ranges (+/-2g, +/-250 dps)
ACCEL_SF = 16384.0   # LSB/g
GYRO_SF  = 131.0     # LSB/(deg/s)

PRINT_HZ = 10        # lines per second
CALIBRATION_TIME = 1.0  # seconds of stillness

def read_word(bus, reg):
    hi = bus.read_byte_data(MPU6050_ADDR, reg)
    lo = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    val = (hi << 8) | lo
    if val > 32767:
        val -= 65536
    return val

def setup_mpu(bus):
    # Wake and configure basic filters/ranges
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.05)
    bus.write_byte_data(MPU6050_ADDR, CONFIG, 0x03)       # DLPF ~44 Hz gyro / 42 Hz accel
    bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, 0x00)   # fastest internal (we poll)
    bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, 0x00) # +/-2g
    bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, 0x00)  # +/-250 dps
    time.sleep(0.05)

def accel_to_angles(ax_g, ay_g, az_g):
    # Roll about X, Pitch about Y
    roll  = math.degrees(math.atan2(ay_g, az_g if abs(az_g) > 1e-8 else 1e-8))
    pitch = math.degrees(math.atan2(-ax_g, math.sqrt(ay_g*ay_g + az_g*az_g)))
    return roll, pitch

def calibrate(bus, seconds=CALIBRATION_TIME):
    """Estimate gyro bias and initial roll/pitch from accel while held still."""
    print("\nCalibrating... keep the hand steady")
    t_end = time.time() + seconds
    gx_sum = gy_sum = gz_sum = 0.0
    n = 0
    # also average accel for a clean initial angle
    ax_sum = ay_sum = az_sum = 0.0

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

def main():
    bus = smbus2.SMBus(1)
    setup_mpu(bus)

    # --- Guided calibration trigger ---
    print("Hold the glove in your neutral reference orientation.")
    input("When steady, press ENTER to calibrate...")
    (bx, by, bz), (roll, pitch) = calibrate(bus)

    # Complementary filter parameters
    alpha = 0.98
    yaw = 0.0  # not printed; left here if you expand later
    dt_target = 1.0 / PRINT_HZ
    t_prev = time.perf_counter()

    # Header
    print("Streaming Roll/Pitch (deg). Ctrl+C to stop.\n")
    print("   ROLL(deg)     PITCH(deg)")
    print("----------------------------")

    try:
        while True:
            # Read sensors
            ax = read_word(bus, ACCEL_XOUT_H) / ACCEL_SF
            ay = read_word(bus, ACCEL_XOUT_H + 2) / ACCEL_SF
            az = read_word(bus, ACCEL_XOUT_H + 4) / ACCEL_SF

            gx = read_word(bus, GYRO_XOUT_H) / GYRO_SF - bx
            gy = read_word(bus, GYRO_XOUT_H + 2) / GYRO_SF - by
            gz = read_word(bus, GYRO_XOUT_H + 4) / GYRO_SF - bz  # kept for completeness

            # Timing
            t_now = time.perf_counter()
            dt = t_now - t_prev
            if dt <= 0: dt = dt_target
            t_prev = t_now

            # Integrate gyro
            roll_g  = roll  + gx * dt
            pitch_g = pitch + gy * dt
            # yaw += gz * dt  # not used here

            # Accel angles
            roll_acc, pitch_acc = accel_to_angles(ax, ay, az)

            # Fuse (complementary)
            roll  = alpha * roll_g  + (1.0 - alpha) * roll_acc
            pitch = alpha * pitch_g + (1.0 - alpha) * pitch_acc

            # If signs feel inverted for your mounting, flip here:
            # roll = -roll
            # pitch = -pitch

            # Minimal, aligned output
            print("   {:+9.2f}      {:+9.2f}".format(roll, pitch), flush=True)

            # Pace to PRINT_HZ
            sleep_for = dt_target - (time.perf_counter() - t_now)
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("I2C error: {}".format(e))
