import time
from picamera2 import Picamera2
from PIL import Image
import st7789

# Initialize ST7789 display
disp = st7789.ST7789(
    height=240,
    width=320,
    rotation=0,
    port=0,
    cs=0,
    dc=25,
    backlight=17,
    spi_speed_hz=60 * 1000 * 1000,
    offset_left=0,
    offset_top=0,
)

disp.begin()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration({"size": (320, 240)})  # Match display resolution
picam2.configure(config)
picam2.start()

print("Starting camera feed to display...")

while True:
    # Capture frame from the camera
    frame = picam2.capture_array()
    image = Image.fromarray(frame)

    # Convert image to RGB (ST7789 does not support RGBA)
    image = image.convert("RGB")

    # Display image on ST7789
    disp.display(image)

    # Optional: Limit frame rate
    time.sleep(0.05)  # Adjust for desired refresh rate
