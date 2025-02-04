from st7789 import ST7789
from PIL import Image, ImageDraw
from time import sleep

display = ST7789(
    port=0,
    cs=0,
    dc=25,
    backlight=17,
    width=320,
    height=240,
    rotation=180,
    spi_speed_hz=10 * 1000 * 1000,
)


#buffer = Image.new("RGB", (320, 240))
#draw = ImageDraw.Draw(buffer)

#draw.rectangle((0, 0, 50, 50), (255, 0, 0))
#draw.rectangle((320 - 50, 0, 320, 50), (0, 255, 0))
#draw.rectangle((0, 240 - 50, 50, 240), (0, 0, 255))
#draw.rectangle((320 - 50, 240 - 50, 320, 240), (255, 255, 0))

#sleep(0.1)

#display.display(buffer)