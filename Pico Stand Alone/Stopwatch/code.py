"""
DESCRIPTION:
This example code will be stopwatch with lap function 
using Raspberry Pi Pico.

AUTHOR   : Cytron Technologies Sdn Bhd
WEBSITE  : www.cytron.io
EMAIL    : support@cytron.io

"""
import board
import busio
import digitalio
import adafruit_ssd1306
import time
import pyRTOS

# Initialize I2C and OLED display
i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Define buttons
button_start_stop_continue = digitalio.DigitalInOut(board.GP20)
button_start_stop_continue.direction = digitalio.Direction.INPUT
button_start_stop_continue.pull = digitalio.Pull.UP

button_lap = digitalio.DigitalInOut(board.GP21)
button_lap.direction = digitalio.Direction.INPUT
button_lap.pull = digitalio.Pull.UP

button_reset = digitalio.DigitalInOut(board.GP22)
button_reset.direction = digitalio.Direction.INPUT
button_reset.pull = digitalio.Pull.UP

# Timer variables
running = False
start_time = 0
elapsed_time = 0
lap_times = []

def update_display():
    oled.fill(0)
    oled.text('Cytron Stopwatch', 15, 0, 1)
    mins, secs = divmod(elapsed_time, 60)
    millis = int((elapsed_time - int(elapsed_time)) * 1000)
    time_str = "{:02}:{:02}.{:03}".format(int(mins), int(secs), millis)
    oled.text(time_str, 35, 10, 1)
    
    for i, lap_time in enumerate(lap_times[-3:], start=1):
        lap_mins, lap_secs = divmod(lap_time, 60)
        lap_millis = int((lap_time - int(lap_time)) * 1000)
        lap_str = "Lap {}: {:02}:{:02}.{:03}".format(len(lap_times) - (3 - i), int(lap_mins), int(lap_secs), lap_millis)
        oled.text(lap_str, 0, 10 + i*10, 1)
    
    oled.text('Start', 0, 55, 1)
    oled.text('Lap', 54, 55, 1)
    oled.text('Reset', 99, 55, 1)
    oled.show()

def task_display(self):
    global running, elapsed_time
    while True:
        if running:
            elapsed_time = time.monotonic() - start_time
        update_display()
        yield [pyRTOS.timeout(0.1)]

def task_buttons(self):
    global running, start_time, elapsed_time, lap_times
    last_button_state = {
        "start_stop_continue": True,
        "lap": True,
        "reset": True
    }

    while True:
        if not button_start_stop_continue.value and last_button_state["start_stop_continue"]:
            if running:
                elapsed_time = time.monotonic() - start_time
                running = False
            else:
                start_time = time.monotonic() - elapsed_time
                running = True
            last_button_state["start_stop_continue"] = False
            time.sleep(0.2)  # Debounce delay
        elif button_start_stop_continue.value:
            last_button_state["start_stop_continue"] = True

        if not button_lap.value and last_button_state["lap"]:
            if running:
                lap_time = time.monotonic() - start_time
                lap_times.append(lap_time)
                print(f"Lap: {len(lap_times)} - Time: {lap_time:.2f} seconds")
            last_button_state["lap"] = False
            time.sleep(0.2)  # Debounce delay
        elif button_lap.value:
            last_button_state["lap"] = True

        if not button_reset.value and last_button_state["reset"]:
            running = False
            elapsed_time = 0
            lap_times = []
            update_display()
            last_button_state["reset"] = False
            time.sleep(0.2)  # Debounce delay
        elif button_reset.value:
            last_button_state["reset"] = True

        yield [pyRTOS.timeout(0.1)]

pyRTOS.add_task(pyRTOS.Task(task_display))
pyRTOS.add_task(pyRTOS.Task(task_buttons))
pyRTOS.start()

