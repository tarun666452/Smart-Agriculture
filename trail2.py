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

# Create analog input channels
moisture_sensor = AnalogIn(ads, ADS.P0)  # Soil Moisture Sensor on A0
ph_sensor = AnalogIn(ads, ADS.P1)        # pH Sensor on A1

# pH Sensor Calibration Constants (Adjust based on your pH sensor calibration)
PH_MIN_VOLTAGE = 0.0   # Voltage at pH 0
PH_MAX_VOLTAGE = 3.3   # Voltage at pH 14

def convert_adc_to_ph(adc_value):
    """Convert ADC value to pH level (Assuming linear calibration)."""
    voltage = adc_value * (PH_MAX_VOLTAGE / 65535)  # Convert ADC value to voltage
    ph_value = (voltage / PH_MAX_VOLTAGE) * 14  # Map voltage to pH scale (0-14)
    return round(ph_value, 2)

while True:
    try:
        # Read temperature and humidity from DHT11
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        # Read soil moisture sensor value
        moisture_value = moisture_sensor.value  # Raw ADC value (0-65535)
        moisture_percentage = (moisture_value / 65535.0) * 100  # Convert to percentage

        # Read pH sensor value and convert to pH level
        ph_adc_value = ph_sensor.value  # Raw ADC value
        ph_level = convert_adc_to_ph(ph_adc_value)  # Convert to pH

        # Print readings
        print(f"Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Soil Moisture: {moisture_percentage:.2f}% | pH Level: {ph_level:.2f}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(1)  # Wait 1 second before next reading
