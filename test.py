#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk     # pip install pillow
import time, math, os, csv
import numpy as np
from ahrs.filters import Madgwick

# ---------------------------
# Config
# ---------------------------
SAMPLE_HZ = 30
CALIBRATION_TIME = 1.0
CSV_FILE = "sign_language_test_data.csv"
IMG_DIR = "./Sign-language-pics"

# ---------------------------
# Mock Data Collector
# ---------------------------
class MockDataCollector:
    """Simulates IMU + flex data using sine waves and noise."""
    def __init__(self):
        self.fuse = Madgwick()
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.bias = (0, 0, 0)
        self.t0 = time.time()

    def calibrate(self):
        print("\n(Mock) Calibrating sensors...")
        time.sleep(CALIBRATION_TIME)
        self.bias = (0.1, -0.05, 0.02)
        print("(Mock) Calibration done.\n")

    def read_sample(self):
        # Simulate time-dependent signals
        t = time.time() - self.t0
        ax = 0.0 + 0.02 * math.sin(2 * math.pi * 0.5 * t)
        ay = 0.0 + 0.02 * math.cos(2 * math.pi * 0.5 * t)
        az = 1.0 + 0.02 * math.sin(2 * math.pi * 0.25 * t)
        gx = 10.0 * math.sin(2 * math.pi * 0.1 * t)
        gy = 8.0 * math.cos(2 * math.pi * 0.1 * t)
        gz = 5.0 * math.sin(2 * math.pi * 0.15 * t)

        gyr = np.array([gx, gy, gz]) * np.pi / 180.0
        acc = np.array([ax, ay, az])
        self.q = self.fuse.updateIMU(q=self.q, gyr=gyr, acc=acc)

        roll = math.degrees(math.atan2(2*(self.q[0]*self.q[1] + self.q[2]*self.q[3]),
                                       1 - 2*(self.q[1]**2 + self.q[2]**2)))
        pitch = math.degrees(math.asin(2*(self.q[0]*self.q[2] - self.q[3]*self.q[1])))
        yaw = math.degrees(math.atan2(2*(self.q[0]*self.q[3] + self.q[1]*self.q[2]),
                                      1 - 2*(self.q[2]**2 + self.q[3]**2)))

        flex_vals = [512 + 100 * math.sin(2 * math.pi * 0.3 * t + i)
                     + np.random.normal(0, 5) for i in range(5)]

        return roll, pitch, yaw, gx, gy, gz, ax, ay, az, *flex_vals

    def close(self):
        print("(Mock) Closing collector.")

# ---------------------------
# GUI
# ---------------------------
class SignLanguageTestGUI:
    def __init__(self, root):
        self.root = root
        self.collector = MockDataCollector()
        self.root.title("Sign Language Data Collector (Mock with Images)")
        self.root.geometry("700x600")

        tk.Label(root, text="Select a letter to record data:", font=("Arial", 16)).pack(pady=10)
        frame = tk.Frame(root)
        frame.pack()

        self.buttons = {}
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            btn = tk.Button(frame, text=letter, width=4, height=2,
                            command=lambda l=letter: self.show_sign(l))
            btn.grid(row=i//8, column=i%8, padx=5, pady=5)
            self.buttons[letter] = btn

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.status = tk.Label(root, text="", font=("Arial", 12))
        self.status.pack(pady=10)

        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                headers = ["label", "roll", "pitch", "yaw", "gx", "gy", "gz",
                           "ax", "ay", "az"] + [f"flex{i}" for i in range(5)]
                writer.writerow(headers)

    def show_sign(self, letter):
        """Display the PNG for the selected sign and ask to record."""
        print(letter)
        img_path = os.path.join(IMG_DIR, f"{letter}.png")
        if os.path.exists(img_path):
            img = Image.open(img_path).convert(mode="RGBA").resize((200, 200))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_img)
        else:
            print(f"no {img_path}")
            self.image_label.config(image='', text=f"(No image found for {letter})")

        if messagebox.askyesno("Start Recording", f"Ready to record data for '{letter}'?"):
            self.record_letter(letter)

    def record_letter(self, letter):
        self.status.config(text=f"Calibrating for letter '{letter}'...")
        self.root.update()
        self.collector.calibrate()
        messagebox.showinfo("Calibration", "Calibration done. Press OK to start recording.")
        self.status.config(text=f"Recording letter '{letter}'...")
        self.root.update()
        duration = 3.0
        n_samples = int(duration * SAMPLE_HZ)
        data = []
        for _ in range(n_samples):
            sample = self.collector.read_sample()
            data.append([letter, *sample])
            time.sleep(1.0/SAMPLE_HZ)
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        self.status.config(text=f"Recorded {n_samples} samples for '{letter}'.")
        messagebox.showinfo("Done", f"Saved {n_samples} mock samples for letter '{letter}'.")

    def on_close(self):
        self.collector.close()
        self.root.destroy()

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    gui = SignLanguageTestGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()

