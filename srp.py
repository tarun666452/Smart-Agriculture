import picamera2
import picamera2.encoders
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
DHT_PIN = 4
LIGHT_SENSOR_PIN = 18
MOISTURE_SENSOR_PIN = 22
MOTOR_RELAY_PIN = 17
LED_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)
GPIO.setup(MOTOR_RELAY_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
DHT_SENSOR = Adafruit_DHT.DHT11
MOISTURE_THRESHOLD = 300
LIGHT_THRESHOLD = 300
camera = picamera2.PiCamera2()
camera.start()
def create_model():
    model = keras.Sequential([
        keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(64, (3, 3), activation='relu'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(128, (3, 3), activation='relu'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model
def train_model(model, dataset, labels):
    model.fit(dataset, labels, epochs=10)
    model.save('crop_model.h5')
model = create_model()
try:
    model.load_weights('crop_model.h5')
except:
    print("Model not trained yet. Please train the model with a dataset.")


def identify_crop(image):
    image = cv2.resize(image, (64, 64))
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    crop_id = np.argmax(predictions)
    return crop_id 

try:
    while True:
        camera.capture('crop_image.jpg')
        image = cv2.imread('crop_image.jpg')
        crop_id = identify_crop(image)
        print(f'Identified crop ID: {crop_id}')
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        light_intensity = GPIO.input(LIGHT_SENSOR_PIN)
        moisture_level = GPIO.input(MOISTURE_SENSOR_PIN)
        print(f'Temperature: {temperature}C Humidity: {humidity}%')
        print(f'Light Intensity: {light_intensity}')
        print(f'Moisture Level: {moisture_level}')
        if moisture_level < MOISTURE_THRESHOLD:
            GPIO.output(MOTOR_RELAY_PIN, GPIO.HIGH)
            print('Motor Pump ON')
        else:
            GPIO.output(MOTOR_RELAY_PIN, GPIO.LOW)
            print('Motor Pump OFF')
        if light_intensity < LIGHT_THRESHOLD:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print('LED ON')
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print('LED OFF')
        time.sleep(2)

except KeyboardInterrupt:
    print('Exiting...')
finally:
    GPIO.cleanup()
    camera.stop()
