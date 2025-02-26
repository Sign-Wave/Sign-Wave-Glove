from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
import sys
import random
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = "mongodb+srv://kylemendes65:signwave1234@signwavesensor.hrn11.mongodb.net/?retryWrites=true&w=majority&appName=SignWaveSensor"
client = MongoClient(MONGO_URI)
db = client['SignWaveSensor']
collection = db['sensor_data']

# Detect if running on Raspberry Pi (Linux-based OS)
is_raspberry_pi = sys.platform.startswith('linux')

if is_raspberry_pi:
    import spidev  # import spidev for real Raspberry Pi
else:
    class MockSPI:
        def open(self, bus, device): pass
        def xfer2(self, data): return [0, 0, 0]
        def close(self): pass

    spidev = MockSPI()
    mock_letter_toggle = True  # Variable to alternate letters

# Initialize Flask and SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialize SPI
spi = spidev.SpiDev() if is_raspberry_pi else spidev
if is_raspberry_pi:
    spi.open(0, 0)
    spi.max_speed_hz = 1350000

def read_flex_sensor(channel):
    """Read ADC value from MCP3008"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    
    if not is_raspberry_pi:
        return random.randint(0, 1100)
    
    return value

def identify_letter(sensor_values):
    """Compare sensor values against stored letter ranges in MongoDB"""
    global mock_letter_toggle
    
    if not is_raspberry_pi:
        mock_letter_toggle = not mock_letter_toggle
        return "A" if mock_letter_toggle else "B"
    
    for entry in collection.find():
        if all(entry[f'flex_sensor_{i+1}_min'] <= sensor_values[i] <= entry[f'flex_sensor_{i+1}_max'] for i in range(5)):
            return entry['letter']
    return None

def emit_sensor_data():
    """Continuously emit sensor data and detected letters"""
    while True:
        sensor_values = [
            read_flex_sensor(0),
            read_flex_sensor(1),
            read_flex_sensor(2),
            read_flex_sensor(3),
            read_flex_sensor(4),
        ]
        detected_letter = identify_letter(sensor_values)
        data = {"flex_values": sensor_values, "detected_letter": detected_letter}
        socketio.emit('sensor_data', data)
        time.sleep(4)

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/translate', methods = ["POST"])
def translate():
    """API to return flex sensor data"""
    str_to_return = "REST"
    time.sleep(1)
    value_0 = read_flex_sensor(0)
    value_1 = read_flex_sensor(1)
    value_2 = read_flex_sensor(2)
    value_3 = read_flex_sensor(3)
    value_4 = read_flex_sensor(4)
    avg_1_to_4 = (value_4 + value_3 + value_2 + value_1)/4
    if (avg_1_to_4 > 900 and value_0 <500):
        str_to_return = "A"
    if (avg_1_to_4 < 100 and value_0 > 900):
        str_to_return = "B"
    return str_to_return


@app.route('/sensor')
def sensor_data():
    sensor_values = [
        read_flex_sensor(0),
        read_flex_sensor(1),
        read_flex_sensor(2),
        read_flex_sensor(3),
        read_flex_sensor(4),
    ]
    detected_letter = identify_letter(sensor_values)
    return jsonify({"flex_values": sensor_values, "detected_letter": detected_letter})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Start server
if __name__ == '__main__':
    socketio.start_background_task(emit_sensor_data)
    socketio.run(app, host='0.0.0.0', port=5000)
