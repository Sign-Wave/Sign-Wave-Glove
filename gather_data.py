import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import threading
from spi_funcs import SPI_DEVICE
import registers as reg

"""THUMB_IMU_CS = 8 # CS_B for Thumb IMU is GPIO8 (CE0) or pin 24
THUMB_IMU = SPI_DEVICE(THUMB_IMU_CS, 0)
INDEX_IMU_CS = 7 # CS_B for index IMU is GPIO7 (CE1) or Pin 26 
INDEX_IMU = SPI_DEVICE(INDEX_IMU_CS, 0)
MIDDLE_IMU_CS = 17 # CS_B for MIDDLE IMU is GPIO17 or Pin 11
MIDDLE_IMU = SPI_DEVICE(MIDDLE_IMU_CS, 0)
RING_IMU_CS = 27 # CS_B for index IMU is GPIO27 or Pin 13
RING_IMU = SPI_DEVICE(RING_IMU_CS, 0)
PINKY_IMU_CS = 22 # CS_B for index IMU is GPIO22 or Pin 15
PINKY_IMU = SPI_DEVICE(PINKY_IMU_CS, 0)

ADC_CS = 23 # CS_B for index IMU is GPIO23 or Pin 16
ADC = SPI_DEVICE(ADC_CS, 0)"""

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

    def read_sensors(self):
        sensor_dict = {
            "THUMB_FLEX":[],
            "THUMB_GYR_X":[],
            "THUMB_ACC_X":[],
            "THUMB_GYR_Y":[],
            "THUMB_ACC_Y":[],
            "THUMB_GYR_Z":[],
            "THUMB_ACC_Z":[],

            "INDEX_FLEX":[],
            "INDEX_GYR_X":[],
            "INDEX_ACC_X":[],
            "INDEX_GYR_Y":[],
            "INDEX_ACC_Y":[],
            "INDEX_GYR_Z":[],
            "INDEX_ACC_Z":[],

            "MIDDLE_FLEX":[],
            "MIDDLE_GYR_X":[],
            "MIDDLE_ACC_X":[],
            "MIDDLE_GYR_Y":[],
            "MIDDLE_ACC_Y":[],
            "MIDDLE_GYR_Z":[],
            "MIDDLE_ACC_Z":[],

            "RING_FLEX":[],
            "RING_GYR_X":[],
            "RING_ACC_X":[],
            "RING_GYR_Y":[],
            "RING_ACC_Y":[],
            "RING_GYR_Z":[],
            "RING_ACC_Z":[],

            "PINKY_FLEX":[],
            "PINKY_GYR_X":[],
            "PINKY_ACC_X":[],
            "PINKY_GYR_Y":[],
            "PINKY_ACC_Y":[],
            "PINKY_GYR_Z":[],
            "PINKY_ACC_Z":[],
        }
        time.sleep(5)
        for i in range(0, 20):
            # TODO implement sensor reading
            pass

        return sensor_dict


    def update_letter(self, letter):
        self.label.config(text=f"{letter}", font=("Arial", 16))
        
    def record_sensors(self):
        self.disable_buttons()
        self.read_sensors()
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

def gui():
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            close_all()
            app.destroy()
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

if __name__ == '__main__':
    gui_thread = threading.Thread(target=gui, name='gui thread')
    gui_thread.start()

