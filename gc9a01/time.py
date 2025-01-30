import time
import RPi.GPIO as GPIO

RST_PIN = 25  # GPIO pin for Reset (Pin 22)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)

print("Resetting screen...")
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(1)
GPIO.output(RST_PIN, GPIO.HIGH)
print("Reset complete.")

# Cleanup GPIO
GPIO.cleanup()
