from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import time
import threading
import random

# ---------------------------------------
#  CONFIG
# ---------------------------------------
PHRASE = "HELLO WORLD IS I NEIL "
LETTER_DELAY = 1
RELAX_DELAY = 3.0
HOST = "0.0.0.0"
PORT = 5000

# Number of fake sensor channels to simulate
FAKE_SENSOR_COUNT = 14   # matches your actual "sensor_data" payloads

# ---------------------------------------
#  SERVER SETUP
# ---------------------------------------
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

translate_thread = None
stop_flag = threading.Event()


def generate_fake_sensor_data():
    """Generate fake data similar to your real sensor_data array."""
    # You can tweak ranges as needed
    return [
        random.randint(0, 1023)     # flex sensors
        if i < 5 else random.uniform(-5, 5)  # IMU-like values
        for i in range(FAKE_SENSOR_COUNT)
    ]


def simulate_translate():
    """
    Sends hard-coded phrase over WebSocket,
    with random sensor data included.
    """
    print("\n[SIM] Starting simulated translation...\n")

    for ch in PHRASE:
        if stop_flag.is_set():
            print("[SIM] Stopping translate thread.")
            return

        if ch == " ":
            # RELAX event
            print("[SIM] Sending RELAX")
            sensor_data = generate_fake_sensor_data()
            socketio.emit("letter_detected", {
                "letter": "RELAX",
                "sensor_data": sensor_data
            })
            time.sleep(RELAX_DELAY)
        else:
            # Regular letter event
            print(f"[SIM] Sending {ch}")
            sensor_data = generate_fake_sensor_data()
            socketio.emit("letter_detected", {
                "letter": ch,
                "sensor_data": sensor_data
            })
            time.sleep(LETTER_DELAY)

    print("\n[SIM] Finished sending message.\n")


@app.route("/start_translate", methods=["POST"])
def start_translate():
    global translate_thread, stop_flag

    print("[API] start_translate called")
    stop_flag.clear()

    if translate_thread and translate_thread.is_alive():
        return jsonify({"status": "already running"}), 400

    translate_thread = threading.Thread(target=simulate_translate)
    translate_thread.start()

    return jsonify({"status": "simulated translation started"})


@app.route("/stop_translate", methods=["POST"])
def stop_translate():
    global stop_flag
    print("[API] stop_translate called")
    stop_flag.set()
    return jsonify({"status": "stopping translate"})


@socketio.on("connect")
def on_connect():
    print("[WS] Client connected.")


@socketio.on("disconnect")
def on_disconnect():
    print("[WS] Client disconnected.")


if __name__ == "__main__":
    print(f"\nRunning test ASL simulation server on {HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT)
