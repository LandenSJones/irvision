import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, CS0
spi.max_speed_hz = 1000000  # 1MHz speed

response = spi.xfer2([0xAA])  # Send test byte
print("SPI Response:", response)
