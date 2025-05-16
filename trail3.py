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

# Moisture Sensor Calibration
MOISTURE_MIN = 30000  # Adjust based on dry soil reading
MOISTURE_MAX = 15000  # Adjust based on wet soil reading

def convert_adc_to_moisture(adc_value):
    """Convert ADC moisture sensor value to percentage."""
    moisture_percentage = (MOISTURE_MIN - adc_value) / (MOISTURE_MIN - MOISTURE_MAX) * 100
    moisture_percentage = max(0, min(100, moisture_percentage))  # Clamp between 0 and 100
    return round(moisture_percentage, 2)

# pH Sensor Calibration
PH_SENSOR_VOLTAGE_REF = 3.3  # Adjust if using 5V
ADS_MAX_VALUE = 65535

def convert_adc_to_ph(adc_value):
    """Convert ADC pH sensor value to pH level based on calibration."""
    voltage = (adc_value / ADS_MAX_VALUE) * PH_SENSOR_VOLTAGE_REF  # Convert ADC to voltage
    ph_value = 7 + ((voltage - 2.5) * 3.5)  # Adjust based on your calibration
    return round(ph_value, 2)

while True:
    try:
        # Read temperature and humidity from DHT11
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        # Read soil moisture sensor value
        moisture_value = moisture_sensor.value  # Raw ADC value (0-65535)
        moisture_percentage = convert_adc_to_moisture(moisture_value)

        # Read pH sensor value and convert to pH level
        ph_adc_value = ph_sensor.value  # Raw ADC value
        ph_level = convert_adc_to_ph(ph_adc_value)

        # Print readings
        print(f"Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Soil Moisture: {moisture_percentage:.2f}% | pH Level: {ph_level:.2f}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(1)  # Wait 1 second before next reading
