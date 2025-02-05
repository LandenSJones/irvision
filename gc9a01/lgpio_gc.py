import spidev
import lgpio
import time

# PINS GC9A01A
'''
VCC 1
GND 6
RST 16
SDA 19
DC  22
SCL 23
CS  24
'''
# PINS ST7789


# Colors
BLUE    =   0x001F
colors = [BLUE]

GC9A01A_TFTWIDTH        =       240
GC9A01A_TFTHEIGHT       =       240
GC9A01A_SWRESET     =       0x01
GC9A01A_RDDID       =       0x04
GC9A01A_RDDST       =       0x09
GC9A01A_SLPIN       =       0x10
GC9A01A_SLPOUT      =       0x11
GC9A01A_PTLON       =       0x12
GC9A01A_NORON       =       0x13
GC9A01A_INVOFF      =       0x20
GC9A01A_INVON       =       0x21
GC9A01A_DISPOFF     =       0x28
GC9A01A_DISPON      =       0x29
GC9A01A_CASET       =       0x2A
GC9A01A_RASET       =       0x2B
GC9A01A_RAMWR       =       0x2C
GC9A01A_PTLAR       =       0x30
GC9A01A_VSCRDEF     =       0x33
GC9A01A_TEOFF       =       0x34
GC9A01A_TEON        =       0x35
GC9A01A_MADCTL      =       0x36
GC9A01A_VSCRSADD    =       0x37
GC9A01A_IDLEOFF     =       0x38
GC9A01A_IDLEON      =       0x39
GC9A01A_COLMOD      =       0x3A
GC9A01A_CONTINUE    =       0x3C
GC9A01A_TEARSET     =       0x44
GC9A01A_GETLINE     =       0x45
GC9A01A_SETBRIGHT   =       0x51
GC9A01A_SETCTRL     =       0x53
GC9A01A1_POWER7     =       0xA7
GC9A01A_TEWC        =       0xBA
GC9A01A1_POWER1     =       0xC1
GC9A01A1_POWER2     =       0xC3
GC9A01A1_POWER3     =       0xC4
GC9A01A1_POWER4     =       0xC9
GC9A01A_RDID1       =       0xDA
GC9A01A_RDID2       =       0xDB
GC9A01A_RDID3       =       0xDC
GC9A01A_FRAMERATE   =       0xE8
GC9A01A_SPI2DATA    =       0xE9
GC9A01A_INREGEN2    =       0xEF
GC9A01A_GAMMA1      =       0xF0
GC9A01A_GAMMA2      =       0xF1
GC9A01A_GAMMA3      =       0xF2
GC9A01A_GAMMA4      =       0xF3
GC9A01A_IFACE       =       0xF6
GC9A01A_INREGEN1    =       0xFE
GC9A01A_BLACK       =       0x0000
GC9A01A_NAVY        =       0x000F
GC9A01A_DARKGREEN   =       0x03E0
GC9A01A_DARKCYAN    =       0x03EF
GC9A01A_MAROON      =       0x7800
GC9A01A_PURPLE      =       0x780F
GC9A01A_OLIVE       =       0x7BE0
GC9A01A_LIGHTGREY   =       0xC618
GC9A01A_DARKGREY    =       0x7BEF
GC9A01A_BLUE        =       0x001F
GC9A01A_GREEN       =       0x07E0
GC9A01A_CYAN        =       0x07FF
GC9A01A_RED         =       0xF800
GC9A01A_MAGENTA     =       0xF81F
GC9A01A_YELLOW      =       0xFFE0
GC9A01A_WHITE       =       0xFFFF
GC9A01A_ORANGE      =       0xFD20
GC9A01A_GREENYELLOW =       0xAFE5
GC9A01A_PINK        =       0xFC18

# Pin configuration
SPI_PORT = 0    # SPI BUS 0 : SPI0
# The SPI_DEVICE = 0 setting tells the Raspberry Pi which chip select (CE) pin to use.
# 0 corresponds to CE0 (GPIO 8, Pin 24).
SPI_DEVICE = 0

DC_PIN = 25     # GPIO 25 (Pin 22) is assigned to the DCX (Data/Command) pin of the display.
RST_PIN = 23    # Reset | GPIO 23 (Pin 16) is used to reset the display.

chip_worker = lgpio.gpiochip_open(0)  # Opens gpiochip0
pins = [RST_PIN, DC_PIN]
for pin in pins:
    lgpio.gpio_claim_output(chip_worker, pin)

class GC9A01:
    def __init__(self, spi_port=SPI_PORT, spi_device=SPI_DEVICE, dc_pin=DC_PIN, rst_pin=RST_PIN, width=240, height=240):
        self.spi_port = spi_port
        self.spi_device = spi_device
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.width = width
        self.height = height

        self._spi_init()

    def _spi_init(self):
        """Initialize SPI interface."""
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.spi_port, self.spi_device)
            self.spi.max_speed_hz = 40000000  # 40 MHz
            self.spi.mode = 0
        except Exception as e:
            print(f"SPI initialization failed: {e}")
            self.close()

    def _write_c(self, cmd):
        lgpio.gpio_write(chip_worker, DC_PIN, 0)
        self.spi.writebytes([cmd])

    def _write_d(self, data):
        lgpio.gpio_write(chip_worker, DC_PIN, 1)
        time.sleep(0.1)
        if isinstance(data, int):
            data = [data]  # Convert to single-element list
        chunk_size = 100  # Maximum SPI transfer size
        for i in range(0, len(data), chunk_size):
            self.spi.xfer2(data[i:i+chunk_size])

    def reset_display(self):
        lgpio.gpio_write(chip_worker, RST_PIN, 0)
        time.sleep(0.1)
        lgpio.gpio_write(chip_worker, RST_PIN, 1)
        time.sleep(0.1)

    def init_display(self):
        self.reset_display()

        # Adafruit sends a software reset first
        self._write_c(GC9A01A_SWRESET)  
        time.sleep(0.15)  # Delay after reset

        # Register configuration based on Adafruit's sequence
        self._write_c(GC9A01A_INREGEN2)
        self._write_d(0x00)

        self._write_c(0xEB)
        self._write_d(0x14)

        self._write_c(GC9A01A_INREGEN1)
        self._write_d(0x00)

        self._write_c(GC9A01A_INREGEN2)
        self._write_d(0x00)

        self._write_c(0xEB)
        self._write_d(0x14)

        self._write_c(0x84)
        self._write_d(0x40)

        self._write_c(0x85)
        self._write_d(0xFF)

        self._write_c(0x86)
        self._write_d(0xFF)

        self._write_c(0x87)
        self._write_d(0xFF)

        self._write_c(0x88)
        self._write_d(0x0A)

        self._write_c(0x89)
        self._write_d(0x21)

        self._write_c(0x8A)
        self._write_d(0x00)

        self._write_c(0x8B)
        self._write_d(0x80)

        self._write_c(0x8C)
        self._write_d(0x01)

        self._write_c(0x8D)
        self._write_d(0x01)

        self._write_c(0x8E)
        self._write_d(0xFF)

        self._write_c(0x8F)
        self._write_d(0xFF)

        # Set display orientation
        self._write_c(GC9A01A_MADCTL)
        self._write_d(0x40 | 0x08)  # MADCTL_MX | MADCTL_BGR

        # Set color format
        self._write_c(GC9A01A_COLMOD)
        self._write_d(0x05)  # 16-bit color (RGB565)

        # Frame rate control
        self._write_c(GC9A01A_FRAMERATE)
        self._write_d(0x34)

        # Power settings
        self._write_c(GC9A01A1_POWER2)
        self._write_d(0x13)

        self._write_c(GC9A01A1_POWER3)
        self._write_d(0x13)

        self._write_c(GC9A01A1_POWER4)
        self._write_d(0x22)

        # Enable display inversion (makes colors more vibrant)
        self._write_c(GC9A01A_INVON)

        # Turn the display on
        self._write_c(GC9A01A_SLPOUT)  
        time.sleep(0.15)

        self._write_c(GC9A01A_DISPON)
        time.sleep(0.15)

        print("Display initialized successfully.")


    def set_address_window(self, x0, y0, x1, y1):
        self._write_c(GC9A01A_CASET)
        self._write_d([x0 >> 8])
        self._write_d([x0 & 0xFF])
        self._write_d([x1 >> 8])
        self._write_d([x1 & 0xFF])  # Column Start/End
        self._write_c(0x00)  # Dummy read (some displays need this)
        print(f"CASET: {hex(x0 >> 8)} {hex(x0 & 0xFF)} {hex(x1 >> 8)} {hex(x1 & 0xFF)}")
        self._write_c(GC9A01A_RASET)
        self._write_d([y0 >> 8])
        self._write_d([y0 & 0xFF])
        self._write_d([y1 >> 8])
        self._write_d([y1 & 0xFF])  # Row Start/End
        print(f"RASET: {hex(y0 >> 8)} {hex(y0 & 0xFF)} {hex(y1 >> 8)} {hex(y1 & 0xFF)}")

    def clear_screen(self, color=0x000, x0=0, y0=0, x1=239, y1=239):
        self.set_address_window(x0, y0, x1, y1)
        self._write_c(GC9A01A_RAMWR)
        color_bytes = [color >> 8, color & 0xFF] * (self.width * self.height)
        self._write_d(color_bytes)
        print(f"Cleared screen with color {hex(color)}")

    def fill_rectangle(self, x0, y0, x1, y1, color):
        """Fill a rectangular area with a single color."""
        self.set_address_window(x0, y0, x1, y1)
        self._write_c(GC9A01A_RAMWR)
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        pixel_count = (x1 - x0) * (y1 - y0)  # Ensure correct count
        color_bytes = [color >> 8, color & 0xFF] * int(pixel_count)
        self._write_d(color_bytes)

        print(f"Drew center square at (x0:{x0}, x1:{x1}, y0:{y0}, y1:{y1}, pixel_count:{pixel_count}) with color {hex(color)}")
        return pixel_count

    def __del__(self):
        self.spi.close()
        lgpio.gpiochip_close(chip_worker)

if __name__ == "__main__":
    screen = GC9A01()
    screen.init_display()
    #for color in colors:
    screen.fill_rectangle(100, 100, 140, 140, color=colors[0])
    screen.clear_screen()
