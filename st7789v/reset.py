import gpiod
import time

def setup_gpio(pin):
    """Set up GPIO pin for output using libgpiod."""
    chip = gpiod.Chip("gpiochip0")  # Use the correct chip
    line = chip.get_line(pin)
    line.request(consumer="st7789-bl", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[1])  # Default ON
    return line

bl_pin = setup_gpio(18)  # Assuming backlight is on GPIO 18

# Toggle Backlight
print("Turning Backlight OFF...")
bl_pin.set_value(0)  # Turn OFF
time.sleep(2)        # Wait 2 seconds


print("Turning Backlight ON...")
bl_pin.set_value(1)
