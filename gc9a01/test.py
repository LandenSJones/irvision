import ST7789 as ST7789
import RPi.GPIO as GPIO
from PIL import Image

RST_PIN = 25  # GPIO pin for Reset (Pin 22)

# Initialize Reset Pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.HIGH)

# Initialize SPI Display
disp = ST7789.ST7789(
    port=0,
    cs=0,  # Chip Select (Pin 24, GPIO8)
    dc=24, # Data/Command (Pin 18, GPIO24)
    rst=25, # Reset (Pin 22, GPIO25)
    backlight=None,
    width=240,
    height=240,
    rotation=180,
    spi_speed_hz=40000000
)

disp.begin()

# Create a solid red image
image = Image.new("RGB", (240, 240), (255, 0, 0))  # Red screen
disp.display(image)

print("If this works, your screen should turn red!")
