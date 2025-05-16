import time
import board
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio
import digitalio

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

# Relay Pin Configuration
relay_1 = digitalio.DigitalInOut(board.D17)  # GPIO 17
relay_2 = digitalio.DigitalInOut(board.D27)  # GPIO 27
relay_1.direction = digitalio.Direction.OUTPUT
relay_2.direction = digitalio.Direction.OUTPUT

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
    voltage = (adc_value / ADS_MAX_VALUE) * PH_SENSOR_VOLTAGE_REF
    ph_value = 7 + ((voltage - 2.5) * 3.5)  # Adjust based on your calibration
    return round(ph_value, 2)

def control_relay(moisture_percentage):
    """Control relay based on moisture level."""
    if moisture_percentage < 60:
        relay_1.value = True  # Turn ON Relay Channel-1
        relay_2.value = True  # Turn ON Relay Channel-2
    elif moisture_percentage > 65:
        relay_1.value = False  # Turn OFF Relay Channel-1
        relay_2.value = False  # Turn OFF Relay Channel-2

while True:
    try:
        # Read temperature and humidity from DHT11
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        # Read soil moisture sensor value
        moisture_value = moisture_sensor.value
        moisture_percentage = convert_adc_to_moisture(moisture_value)

        # Read pH sensor value and convert to pH level
        ph_adc_value = ph_sensor.value
        ph_level = convert_adc_to_ph(ph_adc_value)

        # Control relay based on moisture level
        control_relay(moisture_percentage)

        # Print readings
        print(f"Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Soil Moisture: {moisture_percentage:.2f}% | pH Level: {ph_level:.2f}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(1)  # Wait 1 second before next reading