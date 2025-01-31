import spidev
import RPi.GPIO as GPIO
import time

# Write Commands
SWRESET =   0x01    #	Software Reset
SLPOUT  =   0x11    #	Sleep Out (Wake up the display)
INVON   =   0x21    #	Invert Display Colors
DISPOFF =   0x28    #	Display OFF
DISPON  =   0x29    #	Display ON
CASET   =   0x2A    #	Set Column Address
RASET   =   0x2B    #	Set Row Address
RAMWR   =   0x2C    #	Write Data to GRAM
MADCTL  =   0x36    #	Memory Access Control (sets rotation)
COLMOD  =   0x3A    #	Pixel Format Set (color depth)

# Read Commands
RDID    =   0x04    #   Reads the LCD driver ID             |   3 bytes
RDDS    =   0x09    #   Checks if the display is ON/OFF     |	4 bytes
GTSL    =   0x45    #   Reads the current scanline position |   2 bytes

# Pin configuration
SPI_PORT = 0    # SPI BUS 0 : SPI0
'''
 The SPI_DEVICE = 0 setting tells the Raspberry Pi which chip select (CE) pin to use.
 0 corresponds to CE0 (GPIO 8, Pin 24).
'''
SPI_DEVICE = 0

'''
# GPIO 25 (Pin 22) is assigned to the DCX (Data/Command) pin of the display.
Command (0) → Tells the display to execute an instruction.
Data (1) → Sends pixel data or parameters.
'''
DC_PIN = 25     # Data/Command

'''
GPIO 23 (Pin 16) is used to reset the display.
Pulling this pin low (0) forces the display to restart.
After pulling it high (1), the display initializes.
'''
RST_PIN = 23    # Reset

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
    def __init__(self, spi_p, spi_d, dc_p, rst_p, width=240, height=240):
        self.spi_port = spi_p
        self.spi_device = spi_d
        self.dc_pin = dc_p
        self.rst_pin = rst_p
        self.width=width
        self.height=height

        '''
        This sets the GPIO numbering mode to BCM (Broadcom mode).
        The Raspberry Pi has two ways to refer to GPIO pins:
        BCM Mode → Uses the GPIO numbers (e.g., GPIO 23, GPIO 25).
        BOARD Mode → Uses the physical pin numbers (e.g., Pin 16, Pin 22).
        BCM mode is preferred because it remains consistent across different Raspberry Pi models.
        '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        '''
        This opens an SPI connection on the Raspberry Pi.
        The open(SPI_PORT, SPI_DEVICE) function takes two parameters:
        SPI_PORT = 0 → Uses SPI0 (the primary SPI interface on the Pi).
        SPI_DEVICE = 0 → Uses Chip Select 0 (CE0, GPIO 8, Pin 24).
        '''
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.spi_port, self.spi_device)
            self.spi.max_speed_hz = 40_000_000  # 40 MHz
            self.spi.mode = 0
        except Exception as e:
            print(f"SPI initialization failed: {e}")

    def write_command(self, cmd):
        GPIO.output(self.dc_pin, GPIO.LOW)  # Command mode
        self.spi.writebytes([cmd])
    
    def write_data(self, data):
        GPIO.output(self.dc_pin, GPIO.HIGH)  # Data mode
        # Convert single integer to a list
        if isinstance(data, int):
            data = [data]  # Convert to single-element list
        
        # Ensure it's an iterable (list/bytes) before chunking
        chunk_size = 4096  # Maximum SPI transfer size
        for i in range(0, len(data), chunk_size):
            self.spi.writebytes(data[i:i+chunk_size])  # Send in chunks
        
    def reset_display(self):
        GPIO.output(self.rst_pin, GPIO.LOW)  # Holds the display in reset mode (inactive state).
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.HIGH) # Releases reset, allowing the display to initialize.
        time.sleep(0.1)

    def init_display(self):
        # GC9A01A Initialization Sequence
        self.reset_display()
        self.write_command(SLPOUT)  # Sleep Out
        time.sleep(0.12)
        
        self.write_command(MADCTL)  # Memory Data Access Control
        self.write_data(0x00)  # Set rotation
        
        self.write_command(COLMOD)  # Pixel Format
        self.write_data(0x05)  # 16-bit color (RGB565)

        self.write_command(INVON)  # Display Inversion ON
        self.write_command(DISPON)  # Display ON

    def draw_center_square(self, color=0xF800):
        """Draws a small 50×50 square in the center of the circular screen."""
        x_start, x_end = 95, 145  # Centered in 240x240
        y_start, y_end = 95, 145

        self.write_command(CASET)  # Column Address Set
        self.write_data([0x00, x_start, 0x00, x_end])

        self.write_command(RASET)  # Row Address Set
        self.write_data([0x00, y_start, 0x00, y_end])

        self.write_command(RAMWR)  # Start writing pixel data

        color_bytes = [color >> 8, color & 0xFF] * ((x_end - x_start) * (y_end - y_start))
        print(f"Drawing center square with color {hex(color)}")

        # Send in chunks to prevent buffer overflow
        chunk_size = 1024
        for i in range(0, len(color_bytes), chunk_size):
            self.write_data(color_bytes[i:i+chunk_size])

        print("Center square drawn!")

    def clear_screen(self, color=0x0000):
        self.write_command(CASET)  # Column Address Set
        self.write_data([0x00, 0x00, 0x00, 0xEF])

        self.write_command(RASET)  # Row Address Set
        self.write_data([0x00, 0x00, 0x00, 0xEF])

        self.write_command(RAMWR)  # Start writing pixels
        time.sleep(0.01)  # Small delay to ensure readiness

        color_bytes = [color >> 8, color & 0xFF] * (self.width * self.height)

        print(f"Clearing screen with color {hex(color)}")
        print(f"Sending first 10 bytes: {color_bytes[:10]}")

        # Send data in chunks
        chunk_size = 4096  # Adjust if needed
        for i in range(0, len(color_bytes), chunk_size):
            print(f"Writing chunk {i // chunk_size + 1} of {len(color_bytes) // chunk_size}")
            self.write_data(color_bytes[i:i+chunk_size])

        print("Screen clear completed!")


    def read_data(self, cmd, num_bytes=1):
        GPIO.output(self.dc_pin, GPIO.LOW)  # Command mode
        self.spi.writebytes([cmd])  # Send command
        GPIO.output(self.dc_pin, GPIO.HIGH)  # Switch to data mode

        # Read `num_bytes` response bytes
        response = self.spi.xfer2([0x00] * num_bytes)  
        return response

    def close(self):
        """Closes the SPI connection and cleans up GPIO."""
        self.spi.close()
        GPIO.cleanup()

screen = GC9A01(SPI_PORT, SPI_DEVICE, DC_PIN, RST_PIN)
# Run the driver
screen.init_display()
screen.clear_screen(0x00)
time.sleep(1)
screen.clear_screen(0xFF)
time.sleep(1)
screen.clear_screen(0x11)
time.sleep(1)
screen.clear_screen(0xDD)
time.sleep(1)
screen.clear_screen(0x22)
time.sleep(1)
screen.clear_screen(0xCC)
time.sleep(1)
screen.clear_screen(0x33)
time.sleep(1)
screen.clear_screen(0xBB)
time.sleep(1)
screen.clear_screen(0x44)
time.sleep(1)
screen.clear_screen(0xAA)
time.sleep(1)
screen.clear_screen(0x55)
time.sleep(1)
screen.clear_screen(0x99)
time.sleep(1)
screen.clear_screen(0x66)
time.sleep(1)
screen.clear_screen(0x88)
time.sleep(1)
screen.clear_screen(0x77)
screen.close()