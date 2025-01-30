import ST7789 as ST7789
from PIL import Image

# Initialize display
disp = ST7789.ST7789(
    port=0,
    cs=0,  # Chip Select (CS0, GPIO8)
    dc=24, # Data/Command (GPIO24)
    rst=25, # Reset (GPIO25)
    width=240,
    height=240,
    rotation=180,  # Adjust if needed
    spi_speed_hz=40000000
)

disp.begin()

# Create a solid red image
image = Image.new("RGB", (240, 240), (255, 0, 0))  # Red screen
disp.display(image)

print("If this works, your screen should turn red!")
