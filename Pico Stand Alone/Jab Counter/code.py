import time
import board
import digitalio
import analogio
import neopixel
import usb_cdc
import busio
from adafruit_max7219 import matrices

# Enable the USB serial connection
serial = usb_cdc.console

# Define pins for piezoelectric sensors
piezo1_pin = analogio.AnalogIn(board.A0)
piezo2_pin = analogio.AnalogIn(board.A1)

# Define pin for NeoPixel and number of pixels
PIXEL_PIN = board.GP15
NUM_PIXELS = 144  # Update to 144 pixels

# Initialize the NeoPixel strip
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, auto_write=False)

# Adjusted threshold for increased sensitivity
threshold = 10  # Lower value for higher sensitivity

# Initialize combined jab counter
combined_jab_counter = 0

def get_color(index):
    # Determine the color based on the pixel index
    if index < 48:
        return (0, 255, 0)  # Green
    elif index < 96:
        return (255, 255, 0)  # Yellow
    else:
        return (255, 0, 0)  # Red

def update_neopixels(counter):
    global combined_jab_counter
    
    # Reset NeoPixels
    strip.fill((0, 0, 0))
    
    # Light up the pixels based on the jab count
    for i in range(counter % NUM_PIXELS):
        color = get_color(i)  # Get the color for the current pixel
        strip[i] = color

    # Blink the current pixel in sequence
    current_pixel_index = counter % NUM_PIXELS
    strip[current_pixel_index] = (0, 0, 0)  # Turn off the current pixel
    time.sleep(0.1)
    strip[current_pixel_index] = get_color(current_pixel_index)  # Turn it back on with the correct color
    time.sleep(0.1)

    strip.show()  # Update the strip

def display_number(number):
    display.fill(0)
    number_str = f"{number:4}"  # Ensure the number is right-justified and 4 characters long
    display.text(number_str, 0, 0, 1)
    display.show()

# Initialize the MAX7219 matrix display
mosi = board.GP7
clk = board.GP6
cs = digitalio.DigitalInOut(board.GP5)
spi = busio.SPI(clk, MOSI=mosi)

display = matrices.CustomMatrix(spi, cs, 32, 8)

display.clear_all()

while True:
    sensor_value1 = piezo1_pin.value >> 6  # Convert 16-bit to 10-bit value
    sensor_value2 = piezo2_pin.value >> 6  # Convert 16-bit to 10-bit value

    jab_detected = False

    if sensor_value1 > threshold or sensor_value2 > threshold:
        combined_jab_counter += 1
        jab_detected = True
        update_neopixels(combined_jab_counter)  # Update NeoPixels based on combined jab count
        serial.write(f"Combined Jab Count: {combined_jab_counter}\n".encode())
        display_number(combined_jab_counter)  # Display combined jab count
        time.sleep(0.1)  # Debounce to prevent multiple counts from a single jab

    time.sleep(0.01)  # Small delay to avoid overloading