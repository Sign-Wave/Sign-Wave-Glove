from flask import Flask, jsonify, render_template
import time
import sys
from flask_cors import CORS

# Detect if running on Raspberry Pi (Linux-based OS)
is_raspberry_pi = sys.platform.startswith('linux')

if is_raspberry_pi:
    import spidev  # Use real spidev on Raspberry Pi
else:
    # Mock spidev for Windows
    class MockSPI:
        def open(self, bus, device): pass
        def xfer2(self, data): return [0, 0, 0]  # Simulated ADC response
        def close(self): pass

    spidev = MockSPI()  # Assign the mock version

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize SPI
spi = spidev.SpiDev() if is_raspberry_pi else spidev
if is_raspberry_pi:
    spi.open(0, 0)  # Bus 0, Device 0
    spi.max_speed_hz = 1350000

def read_flex_sensor(channel):
    """Read ADC value from MCP3008"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value if is_raspberry_pi else 100  # Return dummy value on Windows

@app.route('/')
def home():
    """Serve the index.html file"""
    return render_template('index.html')

@app.route('/sensor')
def sensor_data():
    """API to return flex sensor data"""
    return jsonify({
        "flex_value_0": read_flex_sensor(0),
        "flex_value_1": read_flex_sensor(1),
        "flex_value_2": read_flex_sensor(2),
        "flex_value_3": read_flex_sensor(3),
        "flex_value_4": read_flex_sensor(4),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
