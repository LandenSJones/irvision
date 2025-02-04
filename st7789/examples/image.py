#!/usr/bin/env python3
import sys
from PIL import Image
import st7789

image_file = sys.argv[1]

# Create ST7789 LCD display class.
disp = st7789.ST7789(
    height=240,
    width=320,
    rotation=180,
    port=0,
    cs=0,
    dc=25,
    backlight=17,
    spi_speed_hz=60 * 1000 * 1000,
    offset_left=0,
    offset_top=0,
)

# Initialize display.
disp.begin()

# Load an image.
print(f"Loading image: {image_file}...")
image = Image.open(image_file)

# Resize the image
image = image.resize((disp.width, disp.height))

# Draw the image on the display hardware.
print("Drawing image")

disp.display(image)
