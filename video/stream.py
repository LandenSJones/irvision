from picamera2 import Picamera2
from PIL import Image
import time
import numbers
import spidev
import RPi.GPIO as GPIO  # Replace gpiod with RPi.GPIO

# GPIO Pin Configuration
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setwarnings(False)

# ST7789 SPI Commands
ST7789_SWRESET = 0x01
ST7789_MADCTL = 0x36
ST7789_FRMCTR2 = 0xB2
ST7789_COLMOD = 0x3A
ST7789_GCTRL = 0xB7
ST7789_VCOMS = 0xBB
ST7789_LCMCTRL = 0xC0
ST7789_VDVVRHEN = 0xC2
ST7789_VRHS = 0xC3
ST7789_VDVS = 0xC4
ST7789_INVON = 0x21
ST7789_INVOFF = 0x20
ST7789_SLPOUT = 0x11
ST7789_DISPON = 0x29
ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C


class ST7789:
    def __init__(self, port, cs, dc, backlight=None, rst=None, width=240, height=240, rotation=90, invert=True, spi_speed_hz=4000000):
        self._spi = spidev.SpiDev(port, cs)
        self._spi.mode = 0
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = spi_speed_hz

        self._dc = dc
        self._rst = rst
        self._bl = backlight
        self._width = width
        self._height = height
        self._rotation = rotation
        self._invert = invert

        # Setup GPIO Pins
        GPIO.setup(self._dc, GPIO.OUT)
        if self._rst is not None:
            GPIO.setup(self._rst, GPIO.OUT)
        if self._bl is not None:
            GPIO.setup(self._bl, GPIO.OUT)
            GPIO.output(self._bl, GPIO.HIGH)  # Turn backlight on

        self.reset()
        self._init()

    def reset(self):
        """Reset the display if reset pin is connected."""
        if self._rst is not None:
            GPIO.output(self._rst, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self._rst, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self._rst, GPIO.HIGH)
            time.sleep(0.5)

    def send(self, data, is_data=True):
        """Send a command or data to the display."""
        GPIO.output(self._dc, GPIO.HIGH if is_data else GPIO.LOW)
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        self._spi.xfer(data)

    def command(self, data):
        """Send a command byte to the display."""
        self.send(data, is_data=False)

    def data(self, data):
        """Send data bytes to the display."""
        self.send(data, is_data=True)

    def _init(self):
        """Initialize the display."""
        self.command(ST7789_SWRESET)
        time.sleep(0.150)

        self.command(ST7789_MADCTL)
        self.data(0x70)

        self.command(ST7789_FRMCTR2)
        self.data([0x0C, 0x0C, 0x00, 0x33, 0x33])

        self.command(ST7789_COLMOD)
        self.data(0x05)

        self.command(ST7789_GCTRL)
        self.data(0x14)

        self.command(ST7789_VCOMS)
        self.data(0x37)

        self.command(ST7789_LCMCTRL)
        self.data(0x2C)

        self.command(ST7789_VDVVRHEN)
        self.data(0x01)

        self.command(ST7789_VRHS)
        self.data(0x12)

        self.command(ST7789_VDVS)
        self.data(0x20)

        if self._invert:
            self.command(ST7789_INVON)
        else:
            self.command(ST7789_INVOFF)

        self.command(ST7789_SLPOUT)
        self.command(ST7789_DISPON)
        time.sleep(0.100)

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for drawing commands."""
        if x1 is None:
            x1 = self._width - 1
        if y1 is None:
            y1 = self._height - 1

        self.command(ST7789_CASET)
        self.data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.command(ST7789_RASET)
        self.data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.command(ST7789_RAMWR)

    def display(self, image):
        """Display an image on the screen."""
        self.set_window()
        pixelbytes = self.image_to_data(image)
        for i in range(0, len(pixelbytes), 4096):
            self.data(pixelbytes[i : i + 4096])

    def image_to_data(self, image):
        """Convert an image to raw RGB565 bytes."""
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image).convert("RGB")

        pixels = list(image.getdata())
        pixelbytes = bytearray()
        for r, g, b in pixels:
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)
            pixelbytes.append((rgb565 >> 8) & 0xFF)
            pixelbytes.append(rgb565 & 0xFF)

        return bytes(pixelbytes)


# Initialize ST7789 display
disp = ST7789(
    height=240,
    width=320,
    rotation=0,
    port=0,
    cs=0,
    dc=25,
    backlight=17,
    spi_speed_hz=60 * 1000 * 1000,
)

# Initialize Camera
picam2 = Picamera2()
config = picam2.create_preview_configuration({"size": (320, 240)})
picam2.configure(config)
picam2.start()

print("Starting camera feed to display...")

while True:
    frame = picam2.capture_array()
    image = Image.fromarray(frame).convert("RGB")
    image.show()
    disp.display(image)
    time.sleep(0.05)
