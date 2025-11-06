#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import time
import math
import numpy as np
import torch
import joblib
from model import SignWaveNetwork  # must exist same dir
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

CONF_THRESHOLD = 0.75
REFRESH_SECONDS = 2.0

# ---------------------------------
# Mock sensor data generator
# ---------------------------------
def read_mock_data():
    # Simulate IMU orientation drift + flex values
    roll  = random.uniform(-60, 60)
    pitch = random.uniform(-60, 60)
    yaw   = random.uniform(-180, 180)

    gx = random.uniform(-1, 1)
    gy = random.uniform(-1, 1)
    gz = random.uniform(-1, 1)

    ax = random.uniform(-1, 1)
    ay = random.uniform(-1, 1)
    az = random.uniform(0.5, 1.5)

    # Simulate 5 flex sensors between 0-1023
    flex = [random.randint(200, 900) for _ in range(5)]

    return [roll,pitch,yaw,gx,gy,gz,ax,ay,az,*flex]

# ---------------------------------
# Model Prediction
# ---------------------------------
def load_inference_components():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    label_encoder = joblib.load("label_encoder.pkl")
    scaler = joblib.load("scaler.pkl")

    input_dim = scaler.mean_.shape[0]
    model = SignWaveNetwork(input_dim, len(label_encoder.classes_)).to(device)
    model.load_state_dict(torch.load("signwave_model.pth", map_location=device))
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

# ---------------------------------
# GUI
# ---------------------------------
class LiveTestGUI:
    def __init__(self, root):
        self.root = root
        root.title("Mock Live Sign Inference (Laptop Test Mode)")

        self.model, self.scaler, self.label_encoder, self.device = load_inference_components()

        self.label = tk.Label(root, text="Starting...", font=("Arial", 40))
        self.label.pack(pady=8)

        self.conf_label = tk.Label(root, text="", font=("Arial", 18))
        self.conf_label.pack(pady=4)

        self.fig, self.ax = plt.subplots(figsize=(6,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=8)

        self.update_prediction()

    def update_prediction(self):
        data = read_mock_data()
        pred, conf, classes, probs = predict_full(
            self.model, self.scaler, self.label_encoder, self.device, data
        )

        self.label.config(text=f"{pred}")
        self.conf_label.config(
            text=f"confidence: {conf:.2f}",
            fg=("green" if conf >= CONF_THRESHOLD and pred != "RELAX" else "red")
        )

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
        bars[0].set_edgecolor("black")
        bars[0].set_linewidth(2.5)

        self.ax.set_ylim(0, 1.0)
        self.ax.set_ylabel("Probability")
        self.ax.set_title("Top Predictions")

        for bar, p in zip(bars, top_probs):
            self.ax.text(bar.get_x()+bar.get_width()/2,
                         min(0.98, p)+0.01,
                         f"{p:.2f}",
                         ha="center", va="bottom", fontsize=11)

        self.fig.tight_layout()
        self.canvas.draw()

        self.root.after(int(REFRESH_SECONDS * 1000), self.update_prediction)

# ---------------------------------
# MAIN
# ---------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTestGUI(root)
    root.mainloop()

