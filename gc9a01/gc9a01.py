import time
import spidev
import lgpio

# PINS GC9A01A
'''
VCC 1
GND 6
RST 16  | GPIO 23
SDA 19
DC  22  | GPIO 25
SCL 23
CS  24  | GPIO 8
'''

RST_PIN = 23
DC_PIN = 25
# SPI BUS 0 : SPI0
SPI_PORT = 0
# The SPI_DEVICE = 0 setting tells the Raspberry Pi which chip select (CE) pin to use.
# 0 corresponds to CE0 (GPIO 8, Pin 24).
SPI_DEVICE = 0
pins = [RST_PIN, DC_PIN]

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

class GC9A01():
    def __init__(
            self,
            dc=DC_PIN,
            reset=RST_PIN,
            spiD=SPI_DEVICE,
            spiP=SPI_PORT):

        self.width = 240
        self.height = 240
        self.dc = dc
        self.reset = reset
        self.spiD = spiD
        self.spiP = spiP


        self.chip_worker = lgpio.gpiochip_open(0)  # Opens gpiochip0
        for pin in pins:
            lgpio.gpio_claim_output(self.chip_worker, pin)

        self.spi = spidev.SpiDev()
        self.spi.open(self.spiP, self.spiD)
        self.spi.max_speed_hz = 40 * 1000 * 1000  # 40 MHz
        self.spi.mode = 0

        self.hard_reset()
        time.sleep(0.100)

        self._write(0xEF)
        self._write(0xEB, b'\x14')
        self._write(0xFE)   # Inter Register Enable1
        self._write(0xEF)
        self._write(0xEB, b'\x14')
        self._write(0x84, b'\x40')
        self._write(0x85, b'\xFF')
        self._write(0x86, b'\xFF')
        self._write(0x87, b'\xFF')
        self._write(0x88, b'\x0A')
        self._write(0x89, b'\x21')
        self._write(0x8A, b'\x00')
        self._write(0x8B, b'\x80')
        self._write(0x8C, b'\x01')
        self._write(0x8D, b'\x01')
        self._write(0x8E, b'\xFF')
        self._write(0x8F, b'\xFF')
        self._write(0xB6, b'\x00\x00')      # Display Function Control
        self._write(COLMOD, b'\x55')          # COLMOD : Pixel Format Set
        self._write(0x90, b'\x08\x08\x08\x08')
        self._write(0xBD, b'\x06')
        self._write(0xBC, b'\x00')
        self._write(0xFF, b'\x60\x01\x04')
        self._write(0xC3, b'\x13')          # Power Control 2
        self._write(0xC4, b'\x13')          # Power Control 3
        self._write(0xC9, b'\x22')          # Power Control 4
        self._write(0xBE, b'\x11')
        self._write(0xE1, b'\x10\x0E')
        self._write(0xDF, b'\x21\x0c\x02')
        self._write(0xF0, b'\x45\x09\x08\x08\x26\x2A')  # Set Gamma 1
        self._write(0xF1, b'\x43\x70\x72\x36\x37\x6F')  # Set Gamma 2
        self._write(0xF2, b'\x45\x09\x08\x08\x26\x2A')  # Set Gamma 3
        self._write(0xF3, b'\x43\x70\x72\x36\x37\x6F')  # Set Gamma 4
        self._write(0xED, b'\x1B\x0B')
        self._write(0xAE, b'\x77')
        self._write(0xCD, b'\x63')
        self._write(0x70, b'\x07\x07\x04\x0E\x0F\x09\x07\x08\x03')
        self._write(0xE8, b'\x34')          # Frame Rate

        self._write(
            0x62,
            b'\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70')

        self._write(
            0x63,
            b'\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70')

        self._write(0x64, b'\x28\x29\xF1\x01\xF1\x00\x07')
        self._write(
            0x66,
            b'\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00')

        self._write(
            0x67,
            b'\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98')

        self._write(0x74, b'\x10\x85\x80\x00\x00\x4E\x00')
        self._write(0x98, b'\x3e\x07')
        self._write(0x35)   # Tearing effect
        self._write(INVON)   # Display Inversion
        self._write(SLPOUT)   # Sleep out
        time.sleep(0.120)
        self._write(DISPON)   # Display On
        time.sleep(0.20)

    def hard_reset(self):
        self.update_pin_value(RST_PIN, 1)
        time.sleep(0.50)
        self.update_pin_value(RST_PIN, 0)
        time.sleep(0.50)
        self.update_pin_value(RST_PIN, 1)
        time.sleep(0.150)

    def _write(self, command=None, data=None):
        """SPI write to the device: commands and data."""
        if command is not None:
            self.update_pin_value(DC_PIN, 0)
            self.spi.writebytes([command])
        if data is not None:
            self.update_pin_value(DC_PIN, 1)
            if isinstance(data, int):
                data = [data]  # Convert to single-element list
            chunk_size = 100  # Maximum SPI transfer size
            for i in range(0, len(data), chunk_size):
                self.spi.xfer2(data[i:i+chunk_size])

    def update_pin_value(self, pin, value):
        lgpio.gpio_write(self.chip_worker, pin, value)

    def set_address_window(self, x0, y0, x1, y1):
        self._write(CASET, [x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        print(f"CASET: {hex(x0 >> 8)} {hex(x0 & 0xFF)} {hex(x1 >> 8)} {hex(x1 & 0xFF)}")

        self._write(RASET, [y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        print(f"RASET: {hex(y0 >> 8)} {hex(y0 & 0xFF)} {hex(y1 >> 8)} {hex(y1 & 0xFF)}")

    def fill_rectangle_solid(self, x0, y0, x1, y1, color):
        """Fill a rectangular area with a single color."""
        self.set_address_window(x0, y0, x1, y1)
        pixel_count = (x1 - x0) * (y1 - y0)  # Ensure correct count
        color_bytes = [color >> 8, color & 0xFF] * pixel_count
        self._write(RAMWR, color_bytes)

        print(f"Drew center square at (x0:{x0}, x1:{x1}, y0:{y0}, y1:{y1}, pixel_count:{pixel_count}) with color {hex(color)}")
        return pixel_count

    def fill_rectangle_multicolor(self, x0, y0, x1, y1, color):
        """Fill a rectangular area with a gradually changing color."""
        self.set_address_window(x0, y0, x1, y1)
        pixel_count = (x1 - x0) * (y1 - y0)  # Ensure correct count
        color_bytes = []

        for i in range(pixel_count):
            new_color = (color + i) & 0xFFFF  # Ensure color wraps within 16-bit
            color_bytes.extend([new_color >> 8, new_color & 0xFF])

        self._write(RAMWR, color_bytes)


    def clear_screen(self, color=0x000):
        self.set_address_window(0, 0, self.width - 1, self.height - 1)
        color_bytes = [color >> 8, color & 0xFF] * (self.width * self.height)
        self._write(RAMWR, color_bytes)
        print(f"Cleared screen with color {hex(color)}")

    def __del__(self):
        self.spi.close()
        lgpio.gpiochip_close(self.chip_worker)

def format_byte_string(data_list):
    """Convert a list of integers into a formatted byte string."""
    return bytes(data_list)

display = GC9A01(dc=25, reset=23)
display.clear_screen()
display.fill_rectangle_solid(120, 120, 240, 240, 0xFFE0)
display.fill_rectangle_multicolor(0, 0, 121, 120, 0xF81F)
display.fill_rectangle_solid(120, 0, 240, 120, 0xF81F)
display.fill_rectangle_multicolor(0, 120, 120, 240, 0xFFE0)