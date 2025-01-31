import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI0, Chip Select 0
spi.max_speed_hz = 500000  # 500 kHz
spi.mode = 0  # Use SPI Mode 0

response = spi.xfer2([0xAA])  # Send test byte (0xAA)
print(f"SPI response: {response}")

spi.close()
