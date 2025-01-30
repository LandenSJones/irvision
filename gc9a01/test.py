import spidev
import ST7789 as ST7789
from PIL import Image, ImageDraw

# Initialize display
disp = ST7789.ST7789(
    port=0,
    cs=0,  # Chip Select (CS0)
    dc=24, # Data/Command (GPIO24)
    rst=25, # Reset (GPIO25)
    backlight=None,  # Some screens don't need this
    width=240,
    height=240,
    rotation=180,  # Adjust if needed
    spi_speed_hz=40000000
)

disp.begin()

# Create red image
image = Image.new("RGB", (240, 240), (255, 0, 0))  # Red
draw = ImageDraw.Draw(image)
draw.text((50, 100), "GC9A01 Test", fill=(255, 255, 255))

disp.display(image)
print("If this works, your LCD should turn red with text!")
