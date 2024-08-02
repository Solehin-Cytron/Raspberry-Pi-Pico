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

# Create I2C bus
i2c = busio.I2C(board.GP5, board.GP4)

# Create MPU6050 sensor object
mpu = adafruit_mpu6050.MPU6050(i2c)

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

while True:
    start = time.monotonic()

    # Read the accelerometer values
    acceleration = mpu.acceleration

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
