#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import smbus2
import spidev
import time
import math
import numpy as np
import csv
import os
from icecream import ic
from ahrs.filters import Madgwick

# ---------------------------
# Configuration
# ---------------------------
SPI_BUS = 0
SPI_DEV = 0
SPI_MAX_HZ = 1_000_000
FLEX_CHANNELS = [0, 1, 2, 3, 4]

# MPU-6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
ACCEL_SF = 16384.0
GYRO_SF = 131.0

# Collection settings
SAMPLE_HZ = 30
CALIBRATION_TIME = 1.0
CSV_FILE = "sign_language_data.csv"
IMG_DIR = "./Sign-language-pics"

# ---------------------------
# Hardware helpers
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

def calibrate(bus, calibration_time=CALIBRATION_TIME):
    print("\nCalibrating... Keep the device steady.")
    t_end = time.time() + calibration_time
    gx_sum = gy_sum = gz_sum = 0.0
    n = 0
    while time.time() < t_end:
        gx = read_word(bus, GYRO_XOUT_H) / GYRO_SF
        gy = read_word(bus, GYRO_XOUT_H + 2) / GYRO_SF
        gz = read_word(bus, GYRO_XOUT_H + 4) / GYRO_SF
        gx_sum += gx
        gy_sum += gy
        gz_sum += gz
        n += 1
        time.sleep(0.002)
    if n == 0:
        n = 1
    print("Calibration done.\n")
    return gx_sum/n, gy_sum/n, gz_sum/n

# ---------------------------
# Data Collector
# ---------------------------
class DataCollector:
    def __init__(self):
        self.spi = open_spi()
        self.bus = smbus2.SMBus(1)
        setup_mpu(self.bus)
        self.fuse = Madgwick()
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.bias = (0, 0, 0)

    def calibrate(self, calibration_time = CALIBRATION_TIME):
        self.bias = calibrate(self.bus, calibration_time)

    def read_sample(self):
        bx, by, bz = self.bias
        ax = read_word(self.bus, ACCEL_XOUT_H) / ACCEL_SF
        ay = read_word(self.bus, ACCEL_XOUT_H + 2) / ACCEL_SF
        az = read_word(self.bus, ACCEL_XOUT_H + 4) / ACCEL_SF
        gx = read_word(self.bus, GYRO_XOUT_H) / GYRO_SF - bx
        gy = read_word(self.bus, GYRO_XOUT_H + 2) / GYRO_SF - by
        gz = read_word(self.bus, GYRO_XOUT_H + 4) / GYRO_SF - bz

        gyr = np.array([gx, gy, gz]) * np.pi / 180.0
        acc = np.array([ax, ay, az])
        self.q = self.fuse.updateIMU(q=self.q, gyr=gyr, acc=acc)
        

        roll = math.degrees(math.atan2(2*(self.q[0]*self.q[1] + self.q[2]*self.q[3]),
                                       1 - 2*(self.q[1]**2 + self.q[2]**2)))
        pitch = math.degrees(math.asin(2*(self.q[0]*self.q[2] - self.q[3]*self.q[1])))
        yaw = math.degrees(math.atan2(2*(self.q[0]*self.q[3] + self.q[1]*self.q[2]),
                                      1 - 2*(self.q[2]**2 + self.q[3]**2)))

        flex_vals = [read_mcp3008_single(self.spi, ch) for ch in FLEX_CHANNELS]
        #return roll, pitch, yaw, gx, gy, gz, ax, ay, az, *flex_vals
        return gx, gy, gz, ax, ay, az, *flex_vals

    def close(self):
        self.spi.close()
        self.bus.close()

# ---------------------------
# GUI
# ---------------------------
class SignLanguageGUI:
    def __init__(self, root):
        self.root = root
        self.collector = DataCollector()
        self.root.title("Sign Language Data Collector")
        self.root.geometry("700x600")

        self.calibrated = False  # Track whether calibration has been done

        # Instruction Label
        tk.Label(root, text="Select a letter to record:", font=("Arial", 16)).pack(pady=5)

        # --- Calibration Button ---
        self.cal_button = tk.Button(root, text="Calibrate Sensors", font=("Arial", 14),
                                    command=self.calibrate_sensors, bg="#d8f3dc")
        self.cal_button.pack(pady=10)

        frame = tk.Frame(root)
        frame.pack()

        # Letter Buttons
        self.buttons = {}
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            btn = tk.Button(frame, text=letter, width=4, height=2,
                            command=lambda l=letter: self.show_sign(l))
            btn.grid(row=i//8, column=i%8, padx=5, pady=5)
            self.buttons[letter] = btn

        # Sign Image
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        # Countdown
        self.countdown_label = tk.Label(root, text="", font=("Arial", 32), fg="red")
        self.countdown_label.pack()

        # Status Bar
        self.status = tk.Label(root, text="Calibration Required", font=("Arial", 12), fg="red")
        self.status.pack(pady=10)

        # Create CSV if needed
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                headers = ["label", "gx", "gy", "gz",
                           "ax", "ay", "az"] + [f"flex{i}" for i in range(5)]
                writer.writerow(headers)

    # --- Calibration Button Action ---
    def calibrate_sensors(self):
        self.status.config(text="Calibrating... Hold glove still.", fg="orange")
        self.root.update()
        self.collector.calibrate()
        self.calibrated = True
        self.status.config(text="Calibration Complete ✓", fg="green")
        messagebox.showinfo("Calibration", "Sensors have been calibrated.\nYou may now record letters.")

    # --- Show sign image ---
    def show_sign(self, letter):
        if not self.calibrated:
            messagebox.showwarning("Calibration Required", "Please press 'Calibrate Sensors' before recording.")
            return

        img_path = os.path.join(IMG_DIR, f"{letter}.png")
        if os.path.exists(img_path):
            img = Image.open(img_path).convert(mode="RGBA").resize((250, 250))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_img, text="")
        else:
            self.image_label.config(image='', text=f"(No image for {letter})")

        if messagebox.askyesno("Start Recording", f"Record samples for '{letter}'?"):
            self.record_letter(letter)

    # Countdown stays the same
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            self.countdown_label.config(text=str(i))
            self.root.update()
            time.sleep(1)
        self.countdown_label.config(text="Go!")
        self.root.update()
        time.sleep(0.5)
        self.countdown_label.config(text="")

    # --- Record Data (Calibration removed here) ---
    def record_letter(self, letter):
        self.status.config(text=f"Recording '{letter}'...", fg="blue")
        self.root.update()

        duration = 2.0
        n_samples = int(duration * SAMPLE_HZ)
        data = []

        for _ in range(n_samples):
            sample = self.collector.read_sample()
            data.append([letter, *sample])
            time.sleep(1.0 / SAMPLE_HZ)

        ic(data)

        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)

        self.status.config(text=f"Recorded {n_samples} samples for '{letter}'.", fg="green")
        messagebox.showinfo("Done", f"Saved {n_samples} samples for '{letter}'.")

    def on_close(self):
        self.collector.close()
        self.root.destroy()
# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    gui = SignLanguageGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()

