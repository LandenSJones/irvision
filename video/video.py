from st7789 import ST7789

display = ST7789(
    port=0,
    cs=0,
    dc=25,
    backlight=17,
    width=320,
    height=240,
    rotation=180,
    spi_speed_hz=60 * 1000 * 1000,
)