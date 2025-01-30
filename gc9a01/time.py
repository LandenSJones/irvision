import time
import digitalio
import board

rst = digitalio.DigitalInOut(board.D25)
rst.direction = digitalio.Direction.OUTPUT

print("Resetting screen...")
rst.value = False
time.sleep(1)
rst.value = True
print("Reset complete.")
