from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
import sys
from pymongo import MongoClient
from led import led
import signal

RED_PIN = 23
GREEN_PIN = 24

green_led = led(GREEN_PIN)
red_led = led(RED_PIN)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://kylemendes65:signwave1234@signwavesensor.hrn11.mongodb.net/?retryWrites=true&w=majority&appName=SignWaveSensor"
client = MongoClient(MONGO_URI)

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
spi = spidev.SpiDev() if is_raspberry_pi else spidev
if is_raspberry_pi:
    spi.open(0, 0)
    spi.max_speed_hz = 1350000

def read_flex_sensor(channel):
    """Read ADC value from MCP3008"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]

def identify_letter(sensor_values):
    """Compare sensor values against stored letter ranges in MongoDB"""
    try:
        print(f"Sensor values: {sensor_values}")  # Debugging log
        
        for entry in collection.find():  
            # print(f"Checking entry: {entry}")  # Print MongoDB entries for debugging

            match = all(
                int(entry.get(f'flex_sensor_{i+1}_min', 0)) <= sensor_values[i] <= int(entry.get(f'flex_sensor_{i+1}_max', 1023))
                for i in range(5)
            )

            if match:
                detected_letter = entry.get('letter', '?')
                red_led.turn_off()
                green_led.turn_on(2)
                # print(f"Match found! Letter: {detected_letter}")
                return detected_letter

        red_led.turn_on(-1)
        print("No match found in database.")
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
        spi.close()
        sys.exit(0)


@app.route('/')
def home():
    return render_template('index.html')

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
    spi.close()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup)
    socketio.start_background_task(emit_sensor_data)
    socketio.run(app, host='0.0.0.0', port=5000)
    signal.pause()
    
