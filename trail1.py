import time
import board
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio

# Initialize DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D4)

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115 module
ads = ADS.ADS1115(i2c)

# Create an analog input channel on A0 for soil moisture
moisture_sensor = AnalogIn(ads, ADS.P0)

while True:
    try:
        # Read temperature and humidity from DHT11
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        # Read soil moisture sensor value
        moisture_value = moisture_sensor.value  # Raw ADC value (0-65535)

        # Convert to percentage (assuming dry = 0, wet = max ADC value)
        moisture_percentage = (moisture_value / 65535.0) * 100

        # Print readings
        print(f"Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Soil Moisture: {moisture_percentage:.2f}%")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(1)  # Wait 1 seconds before next reading
