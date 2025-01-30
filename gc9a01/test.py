import RPi.GPIO as GPIO
import time

DC_PIN = 24  
RST_PIN = 25  

GPIO.setmode(GPIO.BCM)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RST_PIN, GPIO.OUT)

# Set pins HIGH and read back
GPIO.output(DC_PIN, GPIO.HIGH)
GPIO.output(RST_PIN, GPIO.HIGH)

time.sleep(0.5)  # Small delay

# Read pin values
dc_state = GPIO.input(DC_PIN)
rst_state = GPIO.input(RST_PIN)

print(f"DC Pin (GPIO {DC_PIN}) State: {'HIGH' if dc_state else 'LOW'}")
print(f"RST Pin (GPIO {RST_PIN}) State: {'HIGH' if rst_state else 'LOW'}")

GPIO.cleanup()
