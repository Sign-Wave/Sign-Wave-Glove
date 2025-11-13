#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import math
import json
import threading
from collections import deque
from typing import Dict, Any, List, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# --------------------------------------------------
# Config
# --------------------------------------------------
RANGES_PATH = os.environ.get("ASL_RANGES_PATH", "asl_letter_ranges.json")
HOST = os.environ.get("ASL_HOST", "0.0.0.0")
PORT = int(os.environ.get("ASL_PORT", "5000"))
CORS_ORIGINS = os.environ.get("ASL_CORS_ORIGINS", "*")

SAMPLE_HZ = 30.0           # sensor read frequency
BUFFER_SECONDS = 2.0       # ring buffer duration
TRANSLATE_VOTE_MS = 300    # vote window for translate mode
TRANSLATE_MIN_CONF = 0.60  # min vote ratio to emit letter change
PRACTICE_DEFAULT_MS = 5000 # hold duration for practice
PRACTICE_PASS_CONF = 0.75  # avg confidence threshold
IMU_BOOST_LETTERS = {"C", "J", "Z"}  # letters where IMU matters more

# MCP3008 (flex) config
SPI_BUS = 0
SPI_DEV = 0
SPI_MAX_HZ = 1_000_000
FLEX_CHANNELS = [0, 1, 2, 3, 4]  # thumb..pinky

# MPU-6050 registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
ACCEL_SF = 16384.0   # accel scale factor
GYRO_SF  = 131.0     # gyro scale factor (deg/s)
CALIBRATION_TIME = 1.0  # seconds

ALPHA = 0.98  # complementary filter coefficient

# --------------------------------------------------
# Pi / Dev detection & hardware init
# --------------------------------------------------
IS_PI = sys.platform.startswith("linux")

spi = None
bus = None

if IS_PI:
    try:
        import spidev
        import smbus2

        # SPI for MCP3008
        spi = spidev.SpiDev()
        spi.open(SPI_BUS, SPI_DEV)
        spi.max_speed_hz = SPI_MAX_HZ
        spi.mode = 0b00

        # I2C for MPU6050
        bus = smbus2.SMBus(1)
    except Exception as e:
        print(f"[WARN] Hardware init failed, falling back to mock sensors: {e}")
        spi = None
        bus = None
        IS_PI = False
else:
    spi = None
    bus = None

# --------------------------------------------------
# MCP3008 helpers
# --------------------------------------------------
def read_mcp3008_single(ch: int) -> int:
    """Read one MCP3008 channel (0..7). Returns 0..1023. Mocks data if not on Pi."""
    global spi
    if spi is None:
        # mock values in dev
        base = 700 if ch == 0 else 250 + 30 * ch
        jitter = int((math.sin(time.time() * (ch + 1)) + 1) * 50)
        return max(0, min(1023, base + jitter))

    cmd1 = 0x01
    cmd2 = 0x80 | (ch << 4)
    resp = spi.xfer2([cmd1, cmd2, 0x00])
    return ((resp[1] & 0x03) << 8) | resp[2]

def read_flex_all() -> List[int]:
    return [read_mcp3008_single(ch) for ch in FLEX_CHANNELS]

# --------------------------------------------------
# MPU6050 helpers + complementary filter
# --------------------------------------------------
def mpu_setup():
    global bus
    if bus is None:
        return
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.05)

def mpu_read_word(reg: int) -> int:
    hi = bus.read_byte_data(MPU6050_ADDR, reg)
    lo = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    val = (hi << 8) | lo
    if val > 32767:
        val -= 65536
    return val

def accel_to_angles(ax_g: float, ay_g: float, az_g: float) -> Tuple[float, float]:
    # roll and pitch from accelerometer (deg)
    roll  = math.degrees(math.atan2(ay_g, az_g if abs(az_g) > 1e-8 else 1e-8))
    pitch = math.degrees(math.atan2(-ax_g, math.sqrt(ay_g * ay_g + az_g * az_g)))
    return roll, pitch

def calibrate_imu() -> Tuple[Tuple[float,float,float], Tuple[float,float]]:
    """
    Calibrate gyro bias and initial roll/pitch.
    Returns ((bx,by,bz), (roll0, pitch0)).
    """
    global bus
    if bus is None:
        return (0.0, 0.0, 0.0), (0.0, 0.0)

    print("Calibrating IMU... keep the glove steady")
    t_end = time.time() + CALIBRATION_TIME
    gx_sum = gy_sum = gz_sum = 0.0
    ax_sum = ay_sum = az_sum = 0.0
    n = 0
    while time.time() < t_end:
        ax = mpu_read_word(ACCEL_XOUT_H) / ACCEL_SF
        ay = mpu_read_word(ACCEL_XOUT_H + 2) / ACCEL_SF
        az = mpu_read_word(ACCEL_XOUT_H + 4) / ACCEL_SF
        gx = mpu_read_word(GYRO_XOUT_H) / GYRO_SF
        gy = mpu_read_word(GYRO_XOUT_H + 2) / GYRO_SF
        gz = mpu_read_word(GYRO_XOUT_H + 4) / GYRO_SF
        ax_sum += ax; ay_sum += ay; az_sum += az
        gx_sum += gx; gy_sum += gy; gz_sum += gz
        n += 1
        time.sleep(0.002)

    if n == 0:
        n = 1

    bx = gx_sum / n
    by = gy_sum / n
    bz = gz_sum / n

    ax0 = ax_sum / n
    ay0 = ay_sum / n
    az0 = az_sum / n
    r0, p0 = accel_to_angles(ax0, ay0, az0)

    print("Calibration done.")
    return (bx, by, bz), (r0, p0)

# IMU state
imu_initialized = False
gx_bias = gy_bias = gz_bias = 0.0
roll = pitch = yaw = 0.0
imu_last_t = None

def read_imu() -> Dict[str, float]:
    """
    Returns roll, pitch, yaw, gx, gy, gz, ax, ay, az.
    Uses complementary filter as in your data collection script.
    """
    global imu_initialized, gx_bias, gy_bias, gz_bias, roll, pitch, yaw, imu_last_t, bus

    if bus is None:
        # dev/mock mode
        return {
            "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
            "gx": 0.0, "gy": 0.0, "gz": 0.0,
            "ax": 0.0, "ay": 0.0, "az": 1.0
        }

    if not imu_initialized:
        mpu_setup()
        (gx_bias, gy_bias, gz_bias), (roll0, pitch0) = calibrate_imu()
        roll, pitch, yaw = roll0, pitch0, 0.0
        imu_last_t = time.perf_counter()
        imu_initialized = True

    # Read raw
    ax = mpu_read_word(ACCEL_XOUT_H) / ACCEL_SF
    ay = mpu_read_word(ACCEL_XOUT_H + 2) / ACCEL_SF
    az = mpu_read_word(ACCEL_XOUT_H + 4) / ACCEL_SF
    gx = mpu_read_word(GYRO_XOUT_H) / GYRO_SF - gx_bias
    gy = mpu_read_word(GYRO_XOUT_H + 2) / GYRO_SF - gy_bias
    gz = mpu_read_word(GYRO_XOUT_H + 4) / GYRO_SF - gz_bias

    # dt
    t_now = time.perf_counter()
    dt = t_now - imu_last_t if imu_last_t is not None else 1.0 / SAMPLE_HZ
    imu_last_t = t_now

    # Integrate gyro
    roll_g  = roll  + gx * dt
    pitch_g = pitch + gy * dt
    yaw_g   = yaw   + gz * dt  # basic integration for yaw

    # From accel
    roll_acc, pitch_acc = accel_to_angles(ax, ay, az)

    # Complementary filter for roll/pitch
    roll_new  = ALPHA * roll_g  + (1.0 - ALPHA) * roll_acc
    pitch_new = ALPHA * pitch_g + (1.0 - ALPHA) * pitch_acc
    yaw_new   = yaw_g  # we do not correct yaw with accel

    # update globals
    roll_val  = roll_new
    pitch_val = pitch_new
    yaw_val   = yaw_new

    # store back
    globals()["roll"] = roll_val
    globals()["pitch"] = pitch_val
    globals()["yaw"] = yaw_val

    return {
        "roll": roll_val,
        "pitch": pitch_val,
        "yaw": yaw_val,
        "gx": gx, "gy": gy, "gz": gz,
        "ax": ax, "ay": ay, "az": az
    }

# --------------------------------------------------
# Ranges loading
# --------------------------------------------------
IMU_KEYS = ("roll","pitch","yaw","gx","gy","gz","ax","ay","az")
WEIGHTS = {"flex": 2.0, "imu": 0.5}

def load_ranges(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        data = json.load(f)
    for letter, feats in data.items():
        for k in IMU_KEYS:
            assert k in feats, f"Missing {k} in ranges for {letter}"
        for i in range(5):
            assert f"flex{i}" in feats, f"Missing flex{i} in ranges for {letter}"
    return data

try:
    RANGES = load_ranges(RANGES_PATH)
    RANGES_VERSION = time.strftime("%Y%m%d-%H%M%S", time.localtime(os.path.getmtime(RANGES_PATH)))
except Exception as e:
    print(f"[WARN] Failed to load ranges at startup: {e}")
    RANGES = {}
    RANGES_VERSION = "none"

LETTERS = sorted(RANGES.keys())

# --------------------------------------------------
# Scoring / classification
# --------------------------------------------------
def in_range(val: float, lohi: List[float]) -> bool:
    return lohi[0] <= val <= lohi[1]

def frame_score_for_letter(frame: Dict[str, Any], letter: str) -> Tuple[float, List[int]]:
    """Return (confidence 0..1, per_flex list) comparing frame against a letter's ranges."""
    feats = RANGES.get(letter)
    if not feats:
        return 0.0, [0,0,0,0,0]

    flex = frame["flex"]
    imu = frame["imu"]

    flex_w = WEIGHTS["flex"]
    imu_w = WEIGHTS["imu"]
    if letter in IMU_BOOST_LETTERS:
        imu_w = 1.0

    score = 0.0
    total = 0.0
    per_flex = []

    # flex sensors
    for i in range(5):
        total += flex_w
        ok = in_range(flex[i], feats[f"flex{i}"])
        if ok:
            score += flex_w
        per_flex.append(1 if ok else 0)

    # IMU
    for k in IMU_KEYS:
        total += imu_w
        if in_range(imu[k], feats[k]):
            score += imu_w

    conf = score / total if total else 0.0
    return conf, per_flex

def best_letter_for_frame(frame: Dict[str, Any]) -> Tuple[str, float]:
    best_letter = None
    best_conf = -1.0
    for letter in LETTERS:
        conf, _ = frame_score_for_letter(frame, letter)
        if conf > best_conf:
            best_conf = conf
            best_letter = letter
    if best_conf < 0.55:
        return None, 0.0
    return best_letter, best_conf

# --------------------------------------------------
# Flask + Socket.IO
# --------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})
socketio = SocketIO(app, cors_allowed_origins=CORS_ORIGINS, async_mode="threading")

# ring buffer of recent frames
BUFFER: deque = deque(maxlen=int(SAMPLE_HZ * BUFFER_SECONDS) + 4)
buffer_lock = threading.Lock()
last_letter_emitted = None

def read_one_frame() -> Dict[str, Any]:
    return {
        "t": time.time(),
        "flex": read_flex_all(),
        "imu": read_imu()
    }

def majority_in_window(now: float, ms: int) -> Tuple[str, float]:
    cutoff = now - ms / 1000.0
    with buffer_lock:
        frames = [f for f in list(BUFFER) if f["t"] >= cutoff]
    votes = {}
    total = 0
    for f in frames:
        letter, _ = best_letter_for_frame(f)
        if letter:
            votes[letter] = votes.get(letter, 0) + 1
            total += 1
    if not total:
        return None, 0.0
    winner = max(votes, key=votes.get)
    ratio = votes[winner] / total
    return winner, ratio

def sensor_loop():
    global last_letter_emitted
    interval = 1.0 / SAMPLE_HZ
    last_raw_emit = 0.0
    while True:
        frame = read_one_frame()
        now = frame["t"]

        # store in buffer
        with buffer_lock:
            BUFFER.append(frame)

        # Raw data to client (throttled to ~10Hz)
        if now - last_raw_emit >= 0.1:
            socketio.emit("sensor", {
                "type": "raw",
                "t": frame["t"],
                "flex": frame["flex"],
                "imu": frame["imu"]
            })
            # also emit legacy name for compatibility
            socketio.emit("sensor_data", {
                "flex_values": frame["flex"],
                "detected_letter": None
            })
            last_raw_emit = now

        # Translate mode: majority vote classification
        winner, ratio = majority_in_window(now, TRANSLATE_VOTE_MS)
        if winner and winner != last_letter_emitted and ratio >= TRANSLATE_MIN_CONF:
            last_letter_emitted = winner
            socketio.emit("classification", {
                "type": "letter",
                "t": frame["t"],
                "value": winner,
                "confidence": round(ratio, 3)
            })

        # heartbeat
        socketio.emit("status", {
            "type": "status",
            "ok": True,
            "fps": round(SAMPLE_HZ, 1)
        })

        socketio.sleep(interval)

# --------------------------------------------------
# Practice mode
# --------------------------------------------------
def practice_collect(letter: str, duration_ms: int) -> Dict[str, Any]:
    start = time.time()
    samples: List[Tuple[float, List[int]]] = []

    while (time.time() - start) < (duration_ms / 1000.0):
        with buffer_lock:
            frame = BUFFER[-1] if BUFFER else None
        if frame:
            conf, per = frame_score_for_letter(frame, letter)
            samples.append((conf, per))
        socketio.sleep(1.0 / SAMPLE_HZ)

    if not samples:
        return {
            "type": "practice_result",
            "letter": letter,
            "success": False,
            "error": "no_data",
            "avg_conf": 0.0,
            "samples": 0
        }

    avg_conf = sum(c for c,_ in samples) / len(samples)
    per_flex_majority = [
        1 if sum(p[i] for _,p in samples) > len(samples) / 2 else 0
        for i in range(5)
    ]
    success = (avg_conf >= PRACTICE_PASS_CONF) and all(per_flex_majority)

    # tips based on last frame
    tips = []
    names = ["thumb","index","middle","ring","pinky"]
    with buffer_lock:
        last_frame = BUFFER[-1] if BUFFER else None
    if last_frame and letter in RANGES:
        feats = RANGES[letter]
        for i, ok in enumerate(per_flex_majority):
            if not ok:
                v = last_frame["flex"][i]
                lo, hi = feats[f"flex{i}"]
                delta = (lo - v) if v < lo else (v - hi)
                direction = "bend more" if v < lo else "straighten a bit"
                tips.append(f"{names[i]} {direction} by ~{int(abs(delta))}")

    return {
        "type": "practice_result",
        "letter": letter,
        "success": success,
        "avg_conf": round(avg_conf, 3),
        "samples": len(samples),
        "per_flex": per_flex_majority,
        "tips": tips
    }

# --------------------------------------------------
# HTTP routes
# --------------------------------------------------
@app.route("/health")
def health():
    ok = bool(RANGES)
    return jsonify({
        "ok": ok,
        "ranges_version": RANGES_VERSION,
        "buffer_len": len(BUFFER),
        "is_pi": IS_PI
    })

@app.route("/ranges", methods=["GET", "POST"])
def ranges_endpoint():
    global RANGES, RANGES_VERSION, LETTERS
    if request.method == "GET":
        return jsonify({"version": RANGES_VERSION, "ranges": RANGES})

    payload = request.get_json(force=True)
    new_ranges = payload.get("ranges", payload)
    # validate
    for letter, feats in new_ranges.items():
        for k in IMU_KEYS:
            if k not in feats:
                return jsonify({"ok": False, "error": f"missing {k} for {letter}"}), 400
        for i in range(5):
            if f"flex{i}" not in feats:
                return jsonify({"ok": False, "error": f"missing flex{i} for {letter}"}), 400

    RANGES = new_ranges
    LETTERS = sorted(RANGES.keys())
    RANGES_VERSION = payload.get("version", time.strftime("%Y%m%d-%H%M%S"))
    return jsonify({"ok": True, "version": RANGES_VERSION})

@app.route("/letters")
def letters_route():
    return jsonify({"letters": LETTERS})

@app.route("/sensor")
def sensor_route():
    """Simple debugging endpoint: return last frame + best letter."""
    with buffer_lock:
        frame = BUFFER[-1] if BUFFER else None
    if not frame:
        return jsonify({"ok": False, "error": "no_data"}), 503
    letter, conf = best_letter_for_frame(frame)
    return jsonify({
        "ok": True,
        "t": frame["t"],
        "flex": frame["flex"],
        "imu": frame["imu"],
        "detected_letter": letter,
        "confidence": conf
    })

# --------------------------------------------------
# Socket.IO events
# --------------------------------------------------
@socketio.on("connect")
def on_connect():
    print("[INFO] Client connected")
    emit("status", {"type":"status","ok":True,"connected":True})

@socketio.on("disconnect")
def on_disconnect():
    print("[INFO] Client disconnected")

@socketio.on("start")
def on_start(_msg=None):
    emit("status", {"type":"status","ok":True,"loop":"running"})

@socketio.on("practice_begin")
def on_practice_begin(msg):
    letter = msg.get("letter")
    duration_ms = int(msg.get("duration_ms", PRACTICE_DEFAULT_MS))
    if not letter or letter not in RANGES:
        emit("practice_result", {
            "type":"practice_result",
            "letter": letter,
            "success": False,
            "error": "unknown_letter"
        })
        return
    result = practice_collect(letter, duration_ms)
    emit("practice_result", result)

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    global RANGES, RANGES_VERSION, LETTERS
    # reload ranges if needed
    if not RANGES:
        try:
            RANGES = load_ranges(RANGES_PATH)
            RANGES_VERSION = time.strftime("%Y%m%d-%H%M%S", time.localtime(os.path.getmtime(RANGES_PATH)))
            LETTERS = sorted(RANGES.keys())
        except Exception as e:
            print(f"[ERROR] Could not load ranges in main(): {e}")
            RANGES = {}
            LETTERS = []

    # start sensor loop in background
    socketio.start_background_task(sensor_loop)
    print(f"[INFO] ASL server starting on {HOST}:{PORT}, CORS={CORS_ORIGINS}, is_pi={IS_PI}")
    try:
        socketio.run(app, host=HOST, port=PORT)
    finally:
        if spi is not None:
            try:
                spi.close()
            except Exception:
                pass
        if bus is not None:
            try:
                bus.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
