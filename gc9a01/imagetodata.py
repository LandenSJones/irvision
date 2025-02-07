import numpy
from PIL import Image

def image_to_data(image, rotation=0):
    if not isinstance(image, numpy.ndarray):
            # Resize image to 240x240
        image = image.resize((240, 240), Image.Resampling.LANCZOS)
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
    return result.byteswap().tobytes(), image


# Open the image
image = Image.open("cat.jpg")
data = image_to_data(image)