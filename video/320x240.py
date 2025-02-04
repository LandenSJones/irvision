#!/usr/bin/env python3
from PIL import Image, ImageDraw
from st7789 import ST7789

# General
SPI_PORT = 0
SPI_CS = 0
SPI_DC = 25
BACKLIGHT = 17

# Screen dimensions
WIDTH = 320
HEIGHT = 240

buffer = Image.new("RGB", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(buffer)

draw.rectangle((0, 0, 50, 50), (255, 0, 0))
draw.rectangle((320 - 50, 0, 320, 50), (0, 255, 0))
draw.rectangle((0, 240 - 50, 50, 240), (0, 0, 255))
draw.rectangle((320 - 50, 240 - 50, 320, 240), (255, 255, 0))

display = ST7789(
    port=SPI_PORT,
    cs=SPI_CS,
    dc=SPI_DC,
    backlight=BACKLIGHT,
    width=WIDTH,
    height=HEIGHT,
    rotation=180,
    spi_speed_hz=60 * 1000 * 1000,
)

buffer.show()
display.display(buffer)
