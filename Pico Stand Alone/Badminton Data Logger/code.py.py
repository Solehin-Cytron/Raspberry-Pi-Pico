"""
DESCRIPTION:
This example code will log the Raspberry Pi Pico 
accelerometer data on Raspberry Pi Pico.

AUTHOR   : Cytron Technologies Sdn Bhd
WEBSITE  : www.cytron.io
EMAIL    : support@cytron.io

"""
import time
import board
import busio
import digitalio
import adafruit_mpu6050
import sdcardio
import storage
import adafruit_ssd1306

# Create I2C bus for OLED
i2c_oled = busio.I2C(board.GP5, board.GP4)

# Create MPU6050 sensor object using different pins
i2c_sensor = busio.I2C(board.GP27, board.GP26)
mpu = adafruit_mpu6050.MPU6050(i2c_sensor)

# Create an SD card object
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
cs = board.GP15  # Directly use the Pin object

# Initialize the SD card
try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
except OSError as e:
    print("Card init. failed!")
    error(2)

# Set up status LED
write_led = digitalio.DigitalInOut(board.GP9)
write_led.direction = digitalio.Direction.OUTPUT

# Function to handle errors
def error(errno):
    while True:
        for i in range(errno):
            write_led.value = True
            time.sleep(0.1)
            write_led.value = False
            time.sleep(0.1)
        for _ in range(10 - errno):
            time.sleep(0.2)

# Create a new file for logging data
filename = "/sd/activity.CSV"
for i in range(100):
    filename = "/sd/activity{:02d}.CSV".format(i)
    try:
        with open(filename, "x") as f:
            break
    except OSError:
        pass

print("Writing to", filename)
print("x,y,z")

with open(filename, "a") as logfile:
    logfile.write("x,y,z\n")

# Initialize OLED display
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Increase the buffer size to store more data points
BUFFER_SIZE = 10
MAX_WIDTH = 128
buffer_data_x = [0] * BUFFER_SIZE
graphdata_x = [0] * MAX_WIDTH
buffer_index = 0  # Index to keep track of the current position in the buffer
interval = time.monotonic()  # Initialize interval variable

def draw_axes(oled):
    oled.text("100", 0, 30, 1)
    oled.text("50", 6, 45, 1)
    oled.text("0", 12, 57, 1)
    
    for y in range(30, 64):
        oled.pixel(20, y, 1)  # x-axis
    for x in range(20, 120):
        oled.pixel(x, 63, 1)  # y-axis
    
    for y in range(30, 48):
        oled.pixel(19, y, 1)  # horizontal grid lines
    for y in range(48, 64):
        oled.pixel(19, y, 1)

def update_display(oled):
    global buffer_index
    draw_axes(oled)
    
    for i in range(MAX_WIDTH - 1):
        x0 = int(20 + i)
        y0 = int(63 - round(graphdata_x[i]/4))  # Reverse the y-coordinate
        x1 = int(20 + i + 1)
        y1 = int(63 - round(graphdata_x[i + 1]/4))  # Reverse the y-coordinate
        oled.line(x0, y0, x1, y1, 1)

def run_module(duration, oled):
    global buffer_index
    global graphdata_x
    global interval

    if time.monotonic() > interval:
        interval = time.monotonic() + duration

        # Read the accelerometer values
        acceleration = mpu.acceleration
        x_value = acceleration[0] * 10  # Scale factor to fit graph
        buffer_data_x[buffer_index] = x_value
        buffer_index += 1
        
        if buffer_index >= BUFFER_SIZE:
            buffer_index = 0
            for index in range(BUFFER_SIZE-1):
                for graph_index in range(MAX_WIDTH-1):
                    graphdata_x[graph_index] = graphdata_x[graph_index+1]  # Shift the array
                graphdata_x[len(graphdata_x)-1] = buffer_data_x[index]  # Update new data on last array

        # Clear the OLED display
        oled.fill(0)
        update_display(oled)
        oled.show()

        # Log data to SD card
        with open(filename, "a") as logfile:
            logfile.write("{},{},{}\n".format(acceleration[0], acceleration[1], acceleration[2]))

        # Print the values
        print("Acceleration: X={0:0.3f} Y={1:0.3f} Z={2:0.3f} m/s^2".format(acceleration[0], acceleration[1], acceleration[2]))

        # Flash the write LED
        write_led.value = True
        time.sleep(0.01)
        write_led.value = False

        elapsed = time.monotonic() - start
        print("Processing Time: {:.3f} seconds".format(elapsed))

        # Delay to reduce CPU usage
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        start = time.monotonic()  # Initialize start variable
        while True:
            run_module(0.5, oled)  # Update display every 0.5 seconds
    finally:
        oled.fill(0)
        oled.show()

