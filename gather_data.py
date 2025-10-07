import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import time
import threading
from scipy import signal
from i2c_funcs import I2C_SLAVE
from smbus2 import SMBus 
import spidev
import os
import csv
import pandas as pd

import registers as reg

BACK_OF_HAND_IMU_BASE_ADDR = 0x68

PWR_MGMT_1 = 0x6B
IMU_GYR_X = 0x43
IMU_ACC_X = 0x3B

IMU_GYR_Y = 0x45
IMU_ACC_Y = 0x3D

IMU_GYR_Z = 0x47
IMU_ACC_Z = 0x3F

BACK_OF_HAND_IMU = I2C_SLAVE(BACK_OF_HAND_IMU_BASE_ADDR)
bus = None
# ---- Design filter once ----
fs = 130000    # Hz (your sampling rate)
cutoff = 5.0   # Hz (example cutoff)
order = 6

TARGET_LETTER = 'A'

#sos = signal.butter(order, cutoff, btype='low', fs=fs, output='sos')
#zi = signal.sosfilt_zi(sos)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gather Data: Select Letter")
        self.geometry('400x400')

        self.container = tk.Frame(self)
        self.container.pack(fill='both', expand=True)

        self.frames = {}
        for F in (MainScreen, LetterScreen):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainScreen)

    def show_frame(self, frame_name, image_path=None, letter=None):
        frame = self.frames[frame_name]
        if frame_name == LetterScreen:
            frame.update_image(image_path)
            frame.update_letter(letter)
        frame.tkraise()

class MainScreen(tk.Frame):
    def on_button_click(self, letter, controller):
        global TARGET_LETTER
        TARGET_LETTER = letter
        controller.show_frame(LetterScreen, f"Sign-language-pics/{letter}.png", letter)

    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Choose a letter", font=("Arial", 16))
        label.grid(row=0, column=0, columnspan=3, pady=10)
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            btn = ttk.Button(self, text=letter, command=lambda l=letter: self.on_button_click(l, controller), width=5)
            btn.grid(row=1+i//6, column=i%6, padx=5, pady=5)


class LetterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.label = tk.Label(self)
        self.label.pack(pady=10)


        self.img_label = tk.Label(self)
        self.img_label.pack(pady=10)

        self.record_button = ttk.Button(self, text="Record sensors when in position", command=lambda: self.record_sensors())
        self.record_button.pack(pady=10)

        self.back_button = ttk.Button(self, text="Back", command=lambda: controller.show_frame(MainScreen))
        self.back_button.pack(pady=10)


    def disable_buttons(self):
        self.record_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.record_button.config(state=tk.NORMAL)
        self.back_button.config(state=tk.NORMAL)
        print("Done disable_buttons")

    def read_sensors(self, alpha = 0.75, sampling_rate=500, raw_data=0):

        global zi
        global TARGET_LETTER
        
        thumb_flex_val       = 0
        index_flex_val       = 0
        middle_flex_val      = 0
        ring_flex_val        = 0
        pinky_flex_val       = 0
        gyr_x_val            = 0
        gyr_y_val            = 0
        gyr_z_val            = 0
        acc_x_val            = 0
        acc_y_val            = 0
        acc_z_val            = 0
        output_thumb_flex_val  = 0
        output_index_flex_val  = 0
        output_middle_flex_val = 0
        output_ring_flex_val   = 0
        output_pinky_flex_val  = 0
        output_gyr_x_val       = 0
        output_gyr_y_val       = 0
        output_gyr_z_val       = 0
        output_acc_x_val       = 0
        output_acc_y_val       = 0
        output_acc_z_val       = 0

        sensor_dict = {
            "THUMB_FLEX":0,

            "INDEX_FLEX":0,

            "MIDDLE_FLEX":0,

            "RING_FLEX":0,

            "PINKY_FLEX":0,

            "BACK_OF_HAND_GYR_X":0,
            "BACK_OF_HAND_ACC_X":0,
            "BACK_OF_HAND_GYR_Y":0,
            "BACK_OF_HAND_ACC_Y":0,
            "BACK_OF_HAND_GYR_Z":0,
            "BACK_OF_HAND_ACC_Z":0,
            "SIGN": TARGET_LETTER
        }
        temp_sensor_dict = {
            "THUMB_FLEX":[],

            "INDEX_FLEX":[],

            "MIDDLE_FLEX":[],

            "RING_FLEX":[],

            "PINKY_FLEX":[],

            "BACK_OF_HAND_GYR_X":[],
            "BACK_OF_HAND_ACC_X":[],
            "BACK_OF_HAND_GYR_Y":[],
            "BACK_OF_HAND_ACC_Y":[],
            "BACK_OF_HAND_GYR_Z":[],
            "BACK_OF_HAND_ACC_Z":[],
            "SIGN": TARGET_LETTER
        }
        for i in range(0, 20):
            thumb_flex_val         = self.read_flex_sensor(4)
            index_flex_val         = self.read_flex_sensor(0)
            middle_flex_val        = self.read_flex_sensor(1)
            ring_flex_val          = self.read_flex_sensor(3)
            pinky_flex_val         = self.read_flex_sensor(2)
            gyr_x_val              = BACK_OF_HAND_IMU.read_register(IMU_GYR_X)
            gyr_y_val              = BACK_OF_HAND_IMU.read_register(IMU_GYR_Y)
            gyr_z_val              = BACK_OF_HAND_IMU.read_register(IMU_GYR_Z)
            acc_x_val              = BACK_OF_HAND_IMU.read_register(IMU_ACC_X)
            acc_y_val              = BACK_OF_HAND_IMU.read_register(IMU_ACC_Y)
            acc_z_val              = BACK_OF_HAND_IMU.read_register(IMU_ACC_Z)

            output_thumb_flex_val  = thumb_flex_val  if raw_data else alpha*thumb_flex_val+(1-alpha)*output_thumb_flex_val
            output_index_flex_val  = index_flex_val  if raw_data else alpha*index_flex_val+(1-alpha)*output_index_flex_val
            output_middle_flex_val = middle_flex_val if raw_data else alpha*middle_flex_val+(1-alpha)*output_middle_flex_val
            output_ring_flex_val   = ring_flex_val   if raw_data else alpha*ring_flex_val+(1-alpha)*output_ring_flex_val
            output_pinky_flex_val  = pinky_flex_val  if raw_data else alpha*pinky_flex_val+(1-alpha)*output_pinky_flex_val
            output_gyr_x_val       = gyr_x_val       if raw_data else alpha*gyr_x_val+(1-alpha)*output_gyr_x_val
            output_gyr_y_val       = gyr_y_val       if raw_data else alpha*gyr_y_val+(1-alpha)*output_gyr_y_val
            output_gyr_z_val       = gyr_z_val       if raw_data else alpha*gyr_z_val+(1-alpha)*output_gyr_z_val
            output_acc_x_val       = acc_x_val       if raw_data else alpha*acc_x_val+(1-alpha)*output_acc_x_val
            output_acc_y_val       = acc_y_val       if raw_data else alpha*acc_y_val+(1-alpha)*output_acc_y_val
            output_acc_z_val       = acc_z_val       if raw_data else alpha*acc_z_val+(1-alpha)*output_acc_z_val

            temp_sensor_dict["THUMB_FLEX"].append(output_thumb_flex_val)
            temp_sensor_dict["INDEX_FLEX"].append(output_index_flex_val)
            temp_sensor_dict["MIDDLE_FLEX"].append(output_middle_flex_val)
            temp_sensor_dict["RING_FLEX"].append(output_ring_flex_val)
            temp_sensor_dict["PINKY_FLEX"].append(output_pinky_flex_val)
            temp_sensor_dict["BACK_OF_HAND_GYR_X"].append(output_gyr_x_val)
            temp_sensor_dict["BACK_OF_HAND_GYR_Y"].append(output_gyr_y_val)
            temp_sensor_dict["BACK_OF_HAND_GYR_Z"].append(output_gyr_z_val)
            temp_sensor_dict["BACK_OF_HAND_ACC_X"].append(output_acc_x_val)
            temp_sensor_dict["BACK_OF_HAND_ACC_Y"].append(output_acc_y_val)
            temp_sensor_dict["BACK_OF_HAND_ACC_Z"].append(output_acc_z_val)
            time.sleep(1/sampling_rate)

        # Average the sensor readings
        if raw_data:
            return temp_sensor_dict
        else:
            for keys, values in temp_sensor_dict.items():
                if keys == "SIGN":
                    continue
                sensor_dict[keys] = sum(values)/len(values)
            return sensor_dict

    def save_sensor_readings(self, sensor_dict, filename):

        df = pd.DataFrame([sensor_dict])

        if os.path.exists(filename):
            df.to_csv(filename, mode="a", header=False, index=False) 
        else:
            df.to_csv(filename, mode="w", header=True, index=False) 



    def read_flex_sensor(self, channel):
        """
        Read a single-ended channel (0..7) from MCP3008.
        Returns an integer 0..1023 (10-bit).
        """
        if not (0 <= channel <= 7):
            raise ValueError(f"Channel must be in the range of 0 to 7, was {channel}")
        adc = spi.xfer2([1, 0x80|(channel<<4), 0])
        return ((adc[1] & 3) << 8) + adc[2]

    def update_letter(self, letter):
        global TARGET_LETTER
        TARGET_LETTER = letter
        self.label.config(text=f"{letter}", font=("Arial", 16))

    def get_letter(self):
        global TARGET_LETTER
        return TARGET_LETTER

    def record_sensors(self):
        self.disable_buttons()
        sensors_dict = self.read_sensors(alpha=0.75, sampling_rate=500, raw_data=0)
        print("done training")
        print("sensors dict: ")
        print(sensors_dict)
        self.save_sensor_readings(sensors_dict, "training_data1.csv")
        self.enable_buttons()



    def update_image(self, image_path):
        try:
            image = Image.open(image_path).convert(mode="RGBA")
            image = image.resize((200, 200))
            self.img = ImageTk.PhotoImage(image)

            self.img_label.config(image=self.img)
            self.img_label.image = self.img
        except Exception as e:
            print(f"Error loading image: {e}")

def close_all():
    spi.close()
    sys.exit(0)

def initialize_all():
    print("opening spi")
    spi.open(0, 0)
    spi.max_speed_hz = 1350000
    BACK_OF_HAND_IMU.write_register(PWR_MGMT_1, 0)

def gui():
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            close_all()
            app.destroy()
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()


if __name__ == '__main__':
    bus = SMBus(1)
    spi = spidev.SpiDev()
    gui_thread = threading.Thread(target=gui, name='gui thread')
    gui_thread.start()
    print("initializing")
    initialize_all()

