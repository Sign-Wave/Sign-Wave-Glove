import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import threading

THUMB_IMU = 0
INDEX_IMU = 1
MIDDLE_IMU = 2
RING_IMU =3
PINKY_IMU =4

THUMB_FLEX = 1
INDEX_FLEX = 2
MIDDLE_FLEX = 3
RING_FLEX = 4
PINKY_FLEX = 5


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
        time.sleep(5)
        return


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
    app = App()
    app.mainloop()

if __name__ == '__main__':
    gui_thread = threading.Thread(target=gui, name='gui thread')
    gui_thread.start()
