#!/usr/bin/env python3
import sys
from PIL import Image
import st7789

# Create ST7789 LCD display class.

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

# OV5647 image production while loop
# image = Image.open(image_file)
# image = image.resize((disp.width, disp.height))
# disp.display(image)
