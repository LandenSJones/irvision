# VCC   (Pin 1)   ⚠️  (Try 5V if needed)
# GND   (Pin 6)
# DIN   (Pin 19, BCM 10)
# CLK   (Pin 23, BCM 11) AKA SCK
# CS    (Pin 24, BCM 8)
# DC    (Pin 22, GPIO 25)
# RST   (Pin 18, GPIO 24)
# BL    (Pin 12, GPIO 18)    (Optional)

import numbers
import time
import numpy
from PIL import Image, ImageDraw
import gpiod
import spidev
from enum import Enum

class ST7789Constants(Enum):
    ST7789_NOP = 0x00
    ST7789_SWRESET = 0x01
    ST7789_RDDID = 0x04
    ST7789_RDDST = 0x09

    ST7789_SLPIN = 0x10
    ST7789_SLPOUT = 0x11
    ST7789_PTLON = 0x12
    ST7789_NORON = 0x13

    ST7789_INVOFF = 0x20
    ST7789_INVON = 0x21
    ST7789_DISPOFF = 0x28
    ST7789_DISPON = 0x29

    ST7789_CASET = 0x2A
    ST7789_RASET = 0x2B
    ST7789_RAMWR = 0x2C
    ST7789_RAMRD = 0x2E

    ST7789_PTLAR = 0x30
    ST7789_MADCTL = 0x36
    ST7789_COLMOD = 0x3A

    ST7789_FRMCTR1 = 0xB1
    ST7789_FRMCTR2 = 0xB2
    ST7789_FRMCTR3 = 0xB3
    ST7789_INVCTR = 0xB4
    ST7789_DISSET5 = 0xB6

    ST7789_GCTRL = 0xB7
    ST7789_GTADJ = 0xB8
    ST7789_VCOMS = 0xBB

    ST7789_LCMCTRL = 0xC0
    ST7789_IDSET = 0xC1
    ST7789_VDVVRHEN = 0xC2
    ST7789_VRHS = 0xC3
    ST7789_VDVS = 0xC4
    ST7789_VMCTR1 = 0xC5
    ST7789_FRCTRL2 = 0xC6
    ST7789_CABCCTRL = 0xC7

    ST7789_RDID1 = 0xDA
    ST7789_RDID2 = 0xDB
    ST7789_RDID3 = 0xDC
    ST7789_RDID4 = 0xDD

    ST7789_GMCTRP1 = 0xE0
    ST7789_GMCTRN1 = 0xE1

    ST7789_PWCTR6 = 0xFC


class ST7789(object):
    """Representation of an ST7789 TFT LCD."""

    def __init__(
        self,
        port,
        cs,
        dc,
        backlight=None,
        rst=None,
        width=240,
        height=240,
        rotation=90,
        invert=True,
        spi_speed_hz=1000000,
        offset_left=0,
        offset_top=0,
    ):
        """Create an instance of the display using SPI communication.

        Must provide the GPIO pin number for the D/C pin and the SPI driver.

        Can optionally provide the GPIO pin number for the reset pin as the rst parameter.

        :param port: SPI port number
        :param cs: SPI chip-select number (0 or 1 for BCM
        :param backlight: Pin for controlling backlight
        :param rst: Reset pin for ST7789
        :param width: Width of display connected to ST7789
        :param height: Height of display connected to ST7789
        :param rotation: Rotation of display connected to ST7789
        :param invert: Invert display
        :param spi_speed_hz: SPI speed (in Hz)

        """
        if rotation not in [0, 90, 180, 270]:
            raise ValueError(f"Invalid rotation {rotation}")

        if width != height and rotation in [90, 270]:
            raise ValueError(
                f"Invalid rotation {rotation} for {width}x{height} resolution"
            )

        self._spi = spidev.SpiDev(port, cs)
        self._spi.mode = 0
        self._spi.max_speed_hz = spi_speed_hz

        self._dc = dc
        self._rst = rst
        self._width = width
        self._height = height
        self._rotation = rotation
        self._invert = invert

        self._offset_left = offset_left
        self._offset_top = offset_top

        self._dc = self.setup_gpio(dc, "st7789-dc")
        if backlight is not None:
            self._bl = self.setup_gpio(backlight, "st7789-bl")
            self.set_pin(self._bl, False)
            time.sleep(0.1)
            self.set_pin(self._bl, True)
        if rst is not None:
            self._rst = self.setup_gpio(rst, "st7789-rst")

        self._init()

    def setup_gpio(self, pin, label):
        """Setup a GPIO pin using libgpiod."""
        chip = gpiod.Chip("gpiochip1")
        line = chip.get_line(pin)
        line.request(consumer=label, type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        return line

    def set_pin(self, pin, state):
        pin.set_value(1 if state else 0)  # Directly set pin value

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        self.set_pin(self._dc, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.xfer(data[start:end])

    def set_backlight(self, value):
        """Set the backlight on/off."""
        if self._bl is not None:
            self.set_pin(self._bl, value)

    @property
    def width(self):
        return (
            self._width
            if self._rotation == 0 or self._rotation == 180
            else self._height
        )

    @property
    def height(self):
        return (
            self._height
            if self._rotation == 0 or self._rotation == 180
            else self._width
        )

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            self.set_pin(self._rst, True)
            time.sleep(0.500)
            self.set_pin(self._rst, False)
            time.sleep(0.500)
            self.set_pin(self._rst, True)
            time.sleep(0.500)

    def _init(self):
        # Initialize the display.

        self.command(ST7789Constants.ST7789_SWRESET.value)  # Software reset
        time.sleep(0.150)  # delay 150 ms

        self.command(ST7789Constants.ST7789_MADCTL.value)
        self.data(0x70)

        self.command(ST7789Constants.ST7789_FRMCTR2.value)  # Frame rate ctrl - idle mode
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(ST7789Constants.ST7789_COLMOD.value)
        self.data(0x05)

        self.command(ST7789Constants.ST7789_GCTRL.value)
        self.data(0x14)

        self.command(ST7789Constants.ST7789_VCOMS.value)
        self.data(0x37)

        self.command(ST7789Constants.ST7789_LCMCTRL.value)  # Power control
        self.data(0x2C)

        self.command(ST7789Constants.ST7789_VDVVRHEN.value)  # Power control
        self.data(0x01)

        self.command(ST7789Constants.ST7789_VRHS.value)  # Power control
        self.data(0x12)

        self.command(ST7789Constants.ST7789_VDVS.value)  # Power control
        self.data(0x20)

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(ST7789Constants.ST7789_FRCTRL2.value)
        self.data(0x0F)

        self.command(ST7789Constants.ST7789_GMCTRP1.value)  # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0D)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2B)
        self.data(0x3F)
        self.data(0x54)
        self.data(0x4C)
        self.data(0x18)
        self.data(0x0D)
        self.data(0x0B)
        self.data(0x1F)
        self.data(0x23)

        self.command(ST7789Constants.ST7789_GMCTRN1.value)  # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0C)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2C)
        self.data(0x3F)
        self.data(0x44)
        self.data(0x51)
        self.data(0x2F)
        self.data(0x1F)
        self.data(0x1F)
        self.data(0x20)
        self.data(0x23)

        if self._invert:
            self.command(ST7789Constants.ST7789_INVON.value)  # Invert display
        else:
            self.command(ST7789Constants.ST7789_INVOFF.value)  # Don't invert display

        self.command(ST7789Constants.ST7789_SLPOUT.value)

        self.command(ST7789Constants.ST7789_DISPON.value)  # Display on
        time.sleep(0.100)  # 100 ms

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.command(ST7789Constants.ST7789_CASET.value)  # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)  # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)  # XEND
        self.command(ST7789Constants.ST7789_RASET.value)  # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)  # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)  # YEND
        self.command(ST7789Constants.ST7789_RAMWR.value)  # write to RAM

    def display(self, image):
        """Write the provided image to the hardware.

        :param image: Should be RGB format and the same dimensions as the display hardware.

        """
        # Set address bounds to entire display.
        self.set_window()

        # Convert image to 16bit RGB565 format and
        # flatten into bytes.
        pixelbytes = self.image_to_data(image, self._rotation)

        # Write data to hardware.
        for i in range(0, len(pixelbytes), 4096):
            self.data(pixelbytes[i : i + 4096])

    def image_to_data(self, image, rotation=0):
        if not isinstance(image, numpy.ndarray):
            image = numpy.array(image.convert("RGB"))

        # Rotate the image
        pb = numpy.rot90(image, rotation // 90).astype("uint16")

        # Mask and shift the 888 RGB into 565 RGB
        red = (pb[..., [0]] & 0xF8) << 8
        green = (pb[..., [1]] & 0xFC) << 3
        blue = (pb[..., [2]] & 0xF8) >> 3

        # Stick 'em together
        result = red | green | blue

        # Output the raw bytes
        return result.byteswap().tobytes()

    def __del__(self):
        """Manually close the SPI connection."""
        self._spi.close()
        print("SPIDEV closed")


def main():
    print("hi")
    display = ST7789(0, 0, 25, 18, 24, 320, 240, 0)

    buffer = Image.new("RGB", (320, 240))
    draw = ImageDraw.Draw(buffer)

    draw.rectangle((120, 120, 150, 150), (255, 0, 0))
    display.display(buffer)
    buffer.show(draw)

if __name__ == "__main__":
    main()