from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
import sys
from pymongo import MongoClient
from led import led
import signal
import threading
import model
from enum import Enum
from gather_data2 import DataCollector
import numpy as np

RED_PIN = 23
GREEN_PIN = 24
BUZZER_PIN = 6
SAMPLE_HZ = 7

STABLE_CNT = 15
STABLE_CNT_LOCK = threading.Lock()

TRANSLATE_FSM_THREAD = None
STOP_TRANSLATE = threading.Event()

PRACTICE_THREAD = None
STOP_PRACTICE = threading.Event()

CONF_THRESHOLD = 0.75


green_led = led(GREEN_PIN, active_high=0, default=1, is_input=0)
red_led = led(RED_PIN, active_high=0, default=1, is_input=0)
buzzer = led(BUZZER_PIN, active_high=1, default=0, is_input=0)



# MongoDB Configuration
MONGO_URI = "mongodb+srv://kylemendes65:signwave1234@signwavesensor.hrn11.mongodb.net/?retryWrites=true&w=majority&appName=SignWaveSensor"
client = MongoClient(MONGO_URI)


collect_data = DataCollector(sample_Hz=SAMPLE_HZ)

# Ensure correct database and collection
db = client['asl_data']
collection = db['letters']

# Detect if running on Raspberry Pi (Linux-based OS)
is_raspberry_pi = sys.platform.startswith('linux')

if is_raspberry_pi:
    import spidev
else:
    class MockSPI:
        def open(self, bus, device): pass
        def xfer2(self, data): return [0, 0, 0]
        def close(self): pass
    spidev = MockSPI()

# Initialize Flask and SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialize SPI for MCP3008 (Flex Sensors)
"""
spi = spidev.SpiDev() if is_raspberry_pi else spidev
if is_raspberry_pi:
    spi.open(0, 0)
    spi.max_speed_hz = 1350000
"""

def read_flex_sensor(channel):
    """Read ADC value from MCP3008"""
    collect_data.read_sample()

def identify_letter(sensor_values):
    """Compare sensor values against stored letter ranges in MongoDB"""
    try:
        print(f"Sensor values: {sensor_values}")  # Debugging log
        """ 
        for entry in collection.find():  
            # print(f"Checking entry: {entry}")  # Print MongoDB entries for debugging

           match = all(
                int(entry.get(f'flex_sensor_{i+1}_min', 0)) <= sensor_values[i] <= int(entry.get(f'flex_sensor_{i+1}_max', 1023))
                for i in range(5)
            )

            if (
            if match:
                detected_letter = entry.get('letter', '?')
                red_led.turn_off()
                green_led.turn_on(2)
                # print(f"Match found! Letter: {detected_letter}")
                return detected_letter

        """
        if sensor_values[0]>990 and sensor_values[1] >990 and sensor_values[2]>990 and sensor_values[3]>990 and sensor_values[4] < 500:
            print("A")
            return "A"
        elif sensor_values[0]<500 and sensor_values[1] <500 and sensor_values[2]<500 and sensor_values[3]<500 and sensor_values[4] > 700:
            print("B")
            return "B"

        red_led.turn_on(-1)
        #print("No match found in database.")
    except Exception as e:
        print(f"Error querying MongoDB: {e}")

    return '?'  # Default if no match is found

def emit_sensor_data():
    """Continuously emit sensor data and detected letters"""
    try:
        while True:
            flex_values = [read_flex_sensor(i) for i in range(5)]
            detected_letter = identify_letter(flex_values)
            socketio.emit('sensor_data', {"flex_values": flex_values, "detected_letter": detected_letter})
            time.sleep(1)
    except KeyboardInterrupt:
        green_led.turn_off()
        red_led.turn_off()
        green_led.cleanup()
        red_led.cleanup()
        
        sys.exit(0)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_translate', methods=['POST'])
def start_translate():
    global TRANSLATE_FSM_THREAD
    global STOP_TRANSLATE
    if TRANSLATE_FSM_THREAD and TRANSLATE_FSM_THREAD.is_alive():
        return jsonify({'status':'already running'}), 400
    STOP_TRANSLATE.clear()

    threading.Thread(target=collect_data.calibrate, args=[5]).start()
    for i in range(0, 10):
        red_led.turn_on()
        time.sleep(0.25)
        red_led.turn_off()
        green_led.turn_on()
        time.sleep(0.25)
        green_led.turn_off()
    green_led.turn_on(duration=5)
    TRANSLATE_FSM_THREAD = threading.Thread(target=translate_FSM)
    TRANSLATE_FSM_THREAD.start()
    return jsonify(status="calibrated, and starting the translate FSM")

@app.route('/stop_translate', methods=['POST'])
def stop_translate():
    STOP_TRANSLATE.set()
    return jsonify({'status': 'stopping the translate FSM'})

@app.route('/calibrate', methods=['POST'])
def calibrate_sensors():
    calib_time = 5
    t_end = time.time()+calib_time
    threading.Thread(target=collect_data.calibrate, args=[calib_time]).start()
    while time.time() < t_end:
        red_led.turn_on()
        time.sleep(0.25)
        red_led.turn_off()
        green_led.turn_on()
        time.sleep(0.25)
        green_led.turn_off()
    return jsonify(status="Done calibration")

@app.route("/start_practice", methods=['POST'])
def start_practice():
    global STOP_PRACTICE
    global PRACTICE_THREAD
    STOP_PRACTICE.set()
    if PRACTICE_THREAD and PRACTICE_THREAD.is_alive():
        STOP_PRACTICE.join(timeout=2)
    PRACTICE_THREAD = None

    STOP_PRACTICE.clear()
    red_led.turn_on()

    PRACTICE_THREAD = threading.Thread(target=send_practice_data)
    PRACTICE_THREAD.start()
    return jsonify(status="Starting")
    
    

@app.route("/stop_practice", methods=['POST'])
def stop_practice():
    global STOP_PRACTICE
    STOP_PRACTICE.set()
    red_led.turn_off()
    for _ in range(0, 25):
        green_led.turn_on()
        buzzer.turn_on()
        time.sleep(0.1)
        green_led.turn_off()
        buzzer.turn_off()
        time.sleep(0.1)
    
    return jsonify(status="Stopping")

    


@app.route('/sensor')
def sensor_data():
    """Return sensor data (Flex + Detected Letter)"""
    flex_values = [read_flex_sensor(i) for i in range(5)]
    detected_letter = identify_letter(flex_values)
    return jsonify({"flex_values": flex_values, "detected_letter": detected_letter})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def cleanup(signal_received, frame):
    """Cleanup function to turn off LEDs and close SPI"""
    green_led.turn_off()
    red_led.turn_off()
    green_led.cleanup()
    red_led.cleanup()
    #spi.close()
    collect_data.close()
    sys.exit(0)

class translate_e(Enum):
    LATCH_PARAMS_AND_FLAGS = 0
    DETECT_RELAX = 1
    DETECT_SIGN  = 2
    SEND_SIGN    = 3

def translate_FSM():
    state = translate_e.DETECT_RELAX
    curr_sign = "?"
    curr_data = []
    global STABLE_CNT
    global STOP_TRANSLATE
    global SAMPLE_HZ
    global CONF_THRESHOLD
    __stable_cnt = 15
    __stop_translate = False
    detect_cnt = 0


    ml_model, scaler, label_encoder = model.load_model()


    while not STOP_TRANSLATE.is_set():
        match state:
            case translate_e.LATCH_PARAMS_AND_FLAGS:
                time.sleep(0.5)
                with STABLE_CNT_LOCK:
                    __stable_cnt = STABLE_CNT

                state = translate_e.DETECT_RELAX
            case translate_e.DETECT_RELAX:
                time.sleep(1/SAMPLE_HZ)

                data = collect_data.read_sample()
                np_data = np.array(data, dtype=np.float32)

                detected_label, confidence = model.predict(ml_model, scaler, label_encoder, np_data, CONF_THRESHOLD)
                
                print(f"{time.time()}: Detected letter: {detected_label} (conf: {confidence})")
                print(f"              data: {data}")

                if detected_label == "REST":
                    print(f"Hand Relaxed [{detect_cnt+1}/{__stable_cnt}]")
                    if detect_cnt >= __stable_cnt:
                        print("Detecting stable relaxed, moving on to detecting the sign")
                        detect_cnt = 0
                        socketio.emit('letter_detected', {'letter':'RELAX'})
                        state = translate_e.DETECT_SIGN
                    else:
                        detect_cnt += 1
                else:
                    detect_cnt = 0
            case translate_e.DETECT_SIGN:
                time.sleep(1/SAMPLE_HZ)


                data = collect_data.read_sample()
                np_data = np.array(data, dtype=np.float32)

                detected_label, confidence = model.predict(ml_model, scaler, label_encoder, np_data, CONF_THRESHOLD)
                
                print(f"{time.time()}: Detected letter: {detected_label} (conf: {confidence})")
                print(f"              data: {data}")

                if (detected_label == curr_sign) and (detected_label != "REST") and (confidence > 0.5):
                    curr_sign = detected_label
                    curr_data = data
                    detect_cnt+=1
                    print(f"               [{detect_cnt}/{__stable_cnt}]")
                    if detect_cnt >= __stable_cnt:
                        detect_cnt = 0
                        state = state = translate_e.SEND_SIGN
                else:
                    curr_sign = detected_label
                    curr_data = data
                    detect_cnt = 0


            case translate_e.SEND_SIGN:
                print(f"{time.time()}: Sending detected letter {curr_sign}")
                socketio.emit('letter_detected', {'letter':curr_sign, 'sensor_data':curr_data})
                time.sleep(1)
                state = translate_e.LATCH_PARAMS_AND_FLAGS

    return

class Practice_e(Enum):
    DETECT_SIGN = 0
    SEND_SIGN = 1

def send_practice_data():
    """
    
    """
    curr_sign = "?"
    global STABLE_CNT
    state = Practice_e.DETECT_SIGN
    curr_data = []

    ml_model, scaler, label_encoder = model.load_model()
    detect_cnt = 0

    while not STOP_PRACTICE.is_set():
        match state:
            case Practice_e.DETECT_SIGN:
                time.sleep(1/SAMPLE_HZ)


                data = collect_data.read_sample()
                np_data = np.array(data, dtype=np.float32)

                detected_label, confidence = model.predict(ml_model, scaler, label_encoder, np_data, CONF_THRESHOLD)
                
                print(f"{time.time()}: Detected letter: {detected_label} (conf: {confidence})")
                print(f"              data: {data}")

                if (detected_label == curr_sign) and (detected_label != "REST") and (confidence > 0.4):
                    curr_sign = detected_label
                    curr_data = data
                    detect_cnt+=1
                    print(f"               [{detect_cnt}/{STABLE_CNT}]")
                    if detect_cnt >= STABLE_CNT:
                        detect_cnt = 0
                        state = state = Practice_e.SEND_SIGN
                else:
                    curr_sign = detected_label
                    curr_data = data
                    detect_cnt = 0
                
            case Practice_e.SEND_SIGN:
                print("**************************************************")
                print(f"{time.time()}: Sending detected letter {curr_sign}")
                print("**************************************************")
                socketio.emit('letter_detected', {'letter':curr_sign, 'sensor_data':curr_data})
                time.sleep(0.5)
                state = Practice_e.DETECT_SIGN
    
    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup)
    #socketio.start_background_task(emit_sensor_data)
    socketio.run(app, host='0.0.0.0', port=5000,  allow_unsafe_werkzeug=True)
    signal.pause()
