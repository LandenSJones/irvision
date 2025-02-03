from picamera2 import Picamera2
from PIL import Image

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

# Capture frame
frame = picam2.capture_array()
image = Image.fromarray(frame)

# Convert RGBA to RGB before saving
image = image.convert("RGB")

# Show image (for debugging)
image.show()

# Save as JPEG
image.save("capture.jpg")
