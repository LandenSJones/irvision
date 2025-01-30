from luma.core.interface.serial import i2c
from luma.lcd.device import gc9a01
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw, Image

# Initialize the I2C interface
serial = i2c(port=1, address=0x3C)  # Adjust the address if necessary

# Initialize the GC9A01 display
device = gc9a01(serial)

# Load a font (you can use a different font if you prefer)
font = ImageFont.load_default()

# Create a drawing object
with canvas(device) as draw:
    # Draw some text
    draw.text((10, 10), "Hello, World!", font=font, fill="white")
    
    # Draw a rectangle
    draw.rectangle((10, 30, 100, 50), outline="white", fill="black")
    
    # Draw a line
    draw.line((10, 60, 100, 60), fill="white")

# Keep the script running to display the content
input("Press Enter to exit...")