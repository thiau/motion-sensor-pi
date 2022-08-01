import time
import argparse
import os
import RPi.GPIO as GPIO
from helpers.watson_iot_platform import IBMWatsonIoTPlatform
from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser(
    prog="server.py",
    description='Reads a Motion Sensor and prints the output. Optionally sends the outputs to the Watson IoT Platform (requires service credentials in .env).',
    usage='python3 %(prog)s [options]')

parser.add_argument('--pin', help='The PIN Number your sensor is connected to')
parser.add_argument('--watson', action='store_true', help="Sends outputs of the sensor to the Watson IoT Platform (requires service credentials in .env)")
parser.set_defaults(watson=False)

args = parser.parse_args()

pin = int(args.pin) or int(os.getenv("SENSOR_PIN"))
enable_watson = args.watson or os.getenv(
    'ENABLE_WATSON_IOT_PLATFORM', 'False') == 'True'

iot_platform = IBMWatsonIoTPlatform() if enable_watson else None

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN)

counter = 0

def callback(pin):
    if GPIO.input(pin):
        global counter
        counter = counter + 1
        print(f"Motion Detected.")

        if iot_platform:
            iot_platform.publish(
                event="motionDetected",
                property="motion",
                value=counter)

GPIO.add_event_detect(pin, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(pin, callback)


while True:
    time.sleep(1)