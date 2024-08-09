"""
DESCRIPTION:
This example code will log the accelerometer
data on Raspberry Pi Pico 2.

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
import pyRTOS

# Create I2C bus for OLED
i2c_oled = busio.I2C(board.GP5, board.GP4)

# Create MPU6050 sensor object using different pins
i2c_sensor = busio.I2C(board.GP27, board.GP26)
mpu = adafruit_mpu6050.MPU6050(i2c_sensor)

# Create an SD card object
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
cs = board.GP15


# Initialize the SD card
try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
except OSError as e:
    print("Card init. failed!")
    while True:
        for i in range(2):
            write_led.value = True
            time.sleep(0.1)
            write_led.value = False
            time.sleep(0.1)

# Set up status LED
write_led = digitalio.DigitalInOut(board.GP9)
write_led.direction = digitalio.Direction.OUTPUT

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

# Buffer to store data for the display
BUFFER_SIZE = 10
MAX_WIDTH = 128
buffer_data_x = [0] * BUFFER_SIZE
graphdata_x = [0] * MAX_WIDTH
buffer_index = 0

def draw_axes(oled):
    oled.text("20", 0, 0, 1)
    oled.text("10", 6, 30, 1)
    oled.text("0", 12, 63, 1)
    
    for y in range(0, 64):
        oled.pixel(20, y, 1)  # x-axis
    for x in range(20, 120):
        oled.pixel(x, 63, 1)  # y-axis
    
    for y in range(0, 32):
        oled.pixel(19, y, 1)  # horizontal grid lines
    for y in range(32, 64):
        oled.pixel(19, y, 1)

def update_display(oled):
    global buffer_index
    draw_axes(oled)
    
    for i in range(MAX_WIDTH - 1):
        x0 = int(20 + i)
        y0 = int(63 - round((graphdata_x[i] / 20) * 63))  # Reverse the y-coordinate and scale to fit graph
        x1 = int(20 + i + 1)
        y1 = int(63 - round((graphdata_x[i + 1] / 20) * 63))  # Reverse the y-coordinate and scale to fit graph
        oled.line(x0, y0, x1, y1, 1)

def task_read_sensor(self):
    global buffer_index
    global graphdata_x

    while True:
        # Read the accelerometer values
        acceleration = mpu.acceleration
        x_value = acceleration[0] * 1  # Adjust the scale factor to fit graph with max 20
        buffer_data_x[buffer_index] = x_value
        buffer_index += 1

        if buffer_index >= BUFFER_SIZE:
            buffer_index = 0
            for index in range(BUFFER_SIZE - 1):
                for graph_index in range(MAX_WIDTH - 1):
                    graphdata_x[graph_index] = graphdata_x[graph_index + 1]  # Shift the array
                graphdata_x[len(graphdata_x) - 1] = buffer_data_x[index]  # Update new data on last array

        yield [pyRTOS.timeout(0.05)]  # Read sensor every 0.05 seconds

def task_log_data(self):
    global buffer_index

    while True:
        # Log data to SD card
        with open(filename, "a") as logfile:
            logfile.write("{},{},{}\n".format(buffer_data_x[buffer_index], mpu.acceleration[1], mpu.acceleration[2]))

        # Print the values
        print("Acceleration: X={0:0.3f} Y={1:0.3f} Z={2:0.3f} m/s^2".format(mpu.acceleration[0], mpu.acceleration[1], mpu.acceleration[2]))

        # Flash the write LED
        write_led.value = True
        time.sleep(0.01)
        write_led.value = False

        yield [pyRTOS.timeout(0.5)]  # Log data every 0.5 seconds

def task_display(self):
    while True:
        # Clear the OLED display
        oled.fill(0)
        update_display(oled)
        oled.show()
        yield [pyRTOS.timeout(0.1)]  # Update display every 0.1 seconds

if __name__ == "__main__":
    try:
        pyRTOS.add_task(pyRTOS.Task(task_read_sensor))
        pyRTOS.add_task(pyRTOS.Task(task_log_data))
        pyRTOS.add_task(pyRTOS.Task(task_display))
        pyRTOS.start()
    finally:
        oled.fill(0)
        oled.show()

