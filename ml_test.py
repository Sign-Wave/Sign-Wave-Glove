#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import time
import math
import numpy as np
import torch
import joblib
import smbus2
import spidev
from ahrs.filters import Madgwick
from model import SignWaveNetwork  # your model definition
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import sys

# ---------------------------
# Config
# ---------------------------
SPI_BUS = 0
SPI_DEV = 0
SPI_MAX_HZ = 1_000_000
FLEX_CHANNELS = [0,1,2,3,4]

# MPU-6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
ACCEL_SF = 16384.0
GYRO_SF = 131.0

CONF_THRESHOLD = 0.75
REFRESH_SECONDS = 2.0

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
    lo = bus.read_byte_data(MPU6050_ADDR, reg+1)
    val = (hi << 8) | lo
    if val > 32767:
        val -= 65536
    return val

def setup_mpu(bus):
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.05)

def calibrate_gyro(bus):
    print("Calibrating IMU... Keep still")
    t_end = time.time()+1.0
    gx_sum = gy_sum = gz_sum = 0.0
    n = 0
    while time.time() < t_end:
        gx = read_word(bus, GYRO_XOUT_H)/GYRO_SF
        gy = read_word(bus, GYRO_XOUT_H+2)/GYRO_SF
        gz = read_word(bus, GYRO_XOUT_H+4)/GYRO_SF
        gx_sum += gx; gy_sum += gy; gz_sum += gz
        n += 1
        time.sleep(0.002)
    if n == 0: n = 1
    print("Done.")
    return gx_sum/n, gy_sum/n, gz_sum/n

# ---------------------------
# Model Prediction
# ---------------------------
def load_inference_components():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        label_encoder = joblib.load("label_encoder.pkl")
        scaler = joblib.load("scaler.pkl")
    except Exception as e:
        messagebox.showerror("Missing files", f"Could not load scaler/label encoder: {e}")
        sys.exit(1)

    input_dim = scaler.mean_.shape[0]  # robust way to infer input size
    num_classes = len(label_encoder.classes_)

    model = SignWaveNetwork(input_dim, num_classes).to(device)
    try:
        model.load_state_dict(torch.load("signwave_model.pth", map_location=device))
    except Exception as e:
        messagebox.showerror("Missing model", f"Could not load signwave_model.pth:\n{e}")
        sys.exit(1)
    model.eval()
    return model, scaler, label_encoder, device

def predict_full(model, scaler, label_encoder, device, data_row):
    x = np.array(data_row, dtype=np.float32).reshape(1, -1)
    x = scaler.transform(x)
    x = torch.tensor(x, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1).cpu().numpy().flatten()
    classes = label_encoder.classes_
    pred_idx = int(probs.argmax())
    conf = float(probs[pred_idx])
    pred_label = classes[pred_idx] if conf >= CONF_THRESHOLD else "RELAX"
    return pred_label, conf, classes, probs

# ---------------------------
# GUI
# ---------------------------
class LiveTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Sign Language Inference")

        # Hardware
        self.spi = open_spi()
        self.bus = smbus2.SMBus(1)
        setup_mpu(self.bus)

        # Filter
        self.fuse = Madgwick()
        self.q = np.array([1.0, 0.0, 0.0, 0.0])

        # Calibrate
        self.bias = calibrate_gyro(self.bus)

        # Model bits
        self.model, self.scaler, self.label_encoder, self.device = load_inference_components()

        # UI
        self.label = tk.Label(root, text="Starting...", font=("Arial", 40))
        self.label.pack(pady=8)

        self.conf_label = tk.Label(root, text="", font=("Arial", 18))
        self.conf_label.pack(pady=4)

        # Figure (bar chart)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=8)

        # Start loop
        self.update_prediction()

    def read_data(self):
        bx, by, bz = self.bias
        ax = read_word(self.bus, ACCEL_XOUT_H)     / ACCEL_SF
        ay = read_word(self.bus, ACCEL_XOUT_H + 2) / ACCEL_SF
        az = read_word(self.bus, ACCEL_XOUT_H + 4) / ACCEL_SF

        gx = read_word(self.bus, GYRO_XOUT_H)     / GYRO_SF - bx
        gy = read_word(self.bus, GYRO_XOUT_H + 2) / GYRO_SF - by
        gz = read_word(self.bus, GYRO_XOUT_H + 4) / GYRO_SF - bz

        # Madgwick update
        gyr = np.array([gx, gy, gz]) * np.pi / 180.0
        acc = np.array([ax, ay, az])
        self.q = self.fuse.updateIMU(q=self.q, gyr=gyr, acc=acc)

        roll = math.degrees(math.atan2(2*(self.q[0]*self.q[1] + self.q[2]*self.q[3]),
                                       1 - 2*(self.q[1]**2 + self.q[2]**2)))
        pitch = math.degrees(math.asin(2*(self.q[0]*self.q[2] - self.q[3]*self.q[1])))
        yaw = math.degrees(math.atan2(2*(self.q[0]*self.q[3] + self.q[1]*self.q[2]),
                                      1 - 2*(self.q[2]**2 + self.q[3]**2)))

        flex = [read_mcp3008_single(self.spi, ch) for ch in FLEX_CHANNELS]
        return [roll, pitch, yaw, gx, gy, gz, ax, ay, az, *flex]

    def update_prediction(self):
        data = self.read_data()
        pred, conf, classes, probs = predict_full(
            self.model, self.scaler, self.label_encoder, self.device, data
        )

        # Update text
        self.label.config(text=f"{pred}")
        self.conf_label.config(
            text=f"confidence: {conf:.2f}",
            fg=("green" if conf >= CONF_THRESHOLD and pred != "RELAX" else "red")
        )

        # ---- BAR CHART (TOP-K) ----
        k = min(5, len(classes))
        sorted_idx = np.argsort(probs)[::-1][:k]
        top_classes = classes[sorted_idx]
        top_probs = probs[sorted_idx]

        self.ax.clear()
        bar_colors = []
        for i in range(k):
            if i == 0:
                bar_colors.append("green" if conf >= CONF_THRESHOLD and pred != "RELAX" else "red")
            else:
                bar_colors.append("blue")

        bars = self.ax.bar(top_classes, top_probs, color=bar_colors)
        # Emphasize top bar
        bars[0].set_edgecolor("black")
        bars[0].set_linewidth(2.5)

        self.ax.set_ylim(0, 1.0)
        self.ax.set_ylabel("Probability")
        self.ax.set_title("Top Predictions")
        for bar, p in zip(bars, top_probs):
            self.ax.text(bar.get_x()+bar.get_width()/2, min(0.98, p)+0.01, f"{p:.2f}",
                         ha="center", va="bottom", fontsize=11)

        self.fig.tight_layout()
        self.canvas.draw()

        # schedule next update
        self.root.after(int(REFRESH_SECONDS * 1000), self.update_prediction)

    def on_close(self):
        try:
            self.spi.close()
        except Exception:
            pass
        try:
            self.bus.close()
        except Exception:
            pass
        self.root.destroy()

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTestGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

