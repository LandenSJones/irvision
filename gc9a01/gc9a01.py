import spidev
import RPi.GPIO as GPIO
import time

# PINS
'''
VCC 1
GND 6
RST 16
SDA 19
DC  22
SCL 23
CS  24
'''

# Colors
BLUE    =   0x001F
RED     =   0xF800
GREEN   =   0x07E0
CYAN    =   0x07FF
MAGENTA =   0xF81F
YELLOW  =   0xFFE0
WHITE   =   0xFFFF
colors = [BLUE, RED, GREEN, CYAN, MAGENTA, YELLOW, WHITE]

# Write Commands
SWRESET =   0x01    #	Software Reset
SLPOUT  =   0x11    #	Sleep Out (Wake up the display)
INVON   =   0x21    #	Invert Display Colors
DISPOFF =   0x28    #	Display OFF
DISPON  =   0x29    #	Display ON
CASET   =   0x2A    #	Set Column Address
RASET   =   0x2B    #	Set Row Address
RAMWR   =   0x2C    #	Write Data to GRAM (Graphical RAM)
MADCTL  =   0x36    #	Memory Access Control (sets rotation)
COLMOD  =   0x3A    #	Pixel Format Set (color depth)

# Read Commands
RDID    =   0x04    #   Reads the LCD driver ID             |   3 bytes
RDDS    =   0x09    #   Checks if the display is ON/OFF     |	4 bytes
GTSL    =   0x45    #   Reads the current scanline position |   2 bytes

# Pin configuration
SPI_PORT = 0    # SPI BUS 0 : SPI0
# The SPI_DEVICE = 0 setting tells the Raspberry Pi which chip select (CE) pin to use.
# 0 corresponds to CE0 (GPIO 8, Pin 24).
SPI_DEVICE = 0

DC_PIN = 25     # GPIO 25 (Pin 22) is assigned to the DCX (Data/Command) pin of the display.

RST_PIN = 23    # Reset | GPIO 23 (Pin 16) is used to reset the display.

def color565(red, green=0, blue=0):
    """
    Convert red, green, and blue values (0-255) into a 16-bit 565 encoded color.
    """
    try:
        red, green, blue = red  # Handles tuple input
    except TypeError:
        pass
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | (blue >> 3)

class GC9A01:
    def __init__(self, spi_port=SPI_PORT, spi_device=SPI_DEVICE, dc_pin=DC_PIN, rst_pin=RST_PIN, width=240, height=240):
        self.spi_port = spi_port
        self.spi_device = spi_device
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.width = width
        self.height = height

        self._gpio_init()
        self._spi_init()

    def _gpio_init(self):
        """Initialize GPIO for the display."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)

    def _spi_init(self):
        """Initialize SPI interface."""
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.spi_port, self.spi_device)
            self.spi.max_speed_hz = 10_000_000  # 40 MHz
            self.spi.mode = 0
        except Exception as e:
            print(f"SPI initialization failed: {e}")
            self.close()

    def _write_c(self, cmd):
        GPIO.output(self.dc_pin, GPIO.LOW)  # Command mode
        self.spi.writebytes([cmd])

    def _write_d(self, data):
        GPIO.output(self.dc_pin, GPIO.HIGH)  # Data mode
        if isinstance(data, int):
            data = [data]  # Convert to single-element list
        chunk_size = 100  # Maximum SPI transfer size
        for i in range(0, len(data), chunk_size):
            self.spi.writebytes(data[i:i+chunk_size])

    def reset_display(self):
        GPIO.output(self.rst_pin, GPIO.LOW)  # Holds the display in reset mode (inactive state).
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.HIGH) # Releases reset, allowing the display to initialize.
        time.sleep(0.1)

    def init_display(self):
        # GC9A01A Initialization Sequence
        self.reset_display()
        self._write_c(SLPOUT)  # Sleep Out
        time.sleep(0.1)
        self._write_c(MADCTL)  # Memory Data Access Control
        self._write_d(0x00)       # Set rotation
        self._write_c(COLMOD)  # Pixel Format
        self._write_d(0x05)       # 16-bit color (RGB565)
        self._write_c(INVON)  # Display Inversion ON
        self._write_c(DISPON)  # Display ON

    def set_address_window(self, x0, y0, x1, y1):
        self._write_c(CASET)
        self._write_d([x0 >> 8])
        self._write_d([x0 & 0xFF])
        self._write_d([x1 >> 8])
        self._write_d([x1 & 0xFF])  # Column Start/End
        print(f"CASET: {hex(x0 >> 8)} {hex(x0 & 0xFF)} {hex(x1 >> 8)} {hex(x1 & 0xFF)}")
        self._write_c(RASET)
        self._write_d([y0 >> 8])
        self._write_d([y0 & 0xFF])
        self._write_d([y1 >> 8])
        self._write_d([y1 & 0xFF])  # Row Start/End
        print(f"RASET: {hex(y0 >> 8)} {hex(y0 & 0xFF)} {hex(y1 >> 8)} {hex(y1 & 0xFF)}")

    def clear_screen(self, color=0x000):
        self.set_address_window(0, 0, self.width - 1, self.height - 1)
        self._write_c(RAMWR)
        color_bytes = [color >> 8, color & 0xFF] * (self.width * self.height)
        self._write_d(color_bytes)
        print(f"Cleared screen with color {hex(color)}")

    def close(self):
        self.spi.close()
        GPIO.cleanup()

    def fill_rectangle(self, x0, y0, x1, y1, color):
        """Fill a rectangular area with a single color."""
        self.set_address_window(x0, y0, x1, y1)
        self._write_c(RAMWR)
        pixel_count = (x1 - x0) * (y1 - y0)  # Ensure correct count
        color_bytes = [color >> 8, color & 0xFF] * pixel_count
        self._write_d(color_bytes)

        print(f"Drew center square at (x0:{x0}, x1:{x1}, y0:{y0}, y1:{y1}, pixel_count:{pixel_count}) with color {hex(color)}")
        return pixel_count

if __name__ == "__main__":
    screen = GC9A01()
    screen.init_display()

    for color in colors:
        for i in range(0, 239, 20):
            screen.fill_rectangle(x0=i, y0=i-500, x1=i+20, y1=i+2000, color=color)
            time.sleep(.1)
        screen.clear_screen()

    screen.close()