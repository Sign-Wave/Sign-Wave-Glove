from flask import Flask, jsonify, render_template
import spidev
import time

app = Flask(__name__)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 1350000

def read_flex_sensor(channel):
    """Read ADC value from MCP3008"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value

@app.route('/')
def home():
    """Serve the index.html file"""
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
    """API to return flex sensor data"""
    value_0 = read_flex_sensor(0)
    value_1 = read_flex_sensor(1)
    value_2 = read_flex_sensor(2)
    value_3 = read_flex_sensor(3)
    value_4 = read_flex_sensor(4)
    return jsonify({"flex_value_0": value_0, 
                        "flex_value_1": value_1, 
                        "flex_value_2": value_2, 
                        "flex_value_3": value_3, 
                        "flex_value_4": value_4})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
