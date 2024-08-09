"""
DESCRIPTION:
This example code will counting jump on Raspberry Pi Pico.

AUTHOR   : Cytron Technologies Sdn Bhd
WEBSITE  : www.cytron.io
EMAIL    : support@cytron.io

"""

import board
import digitalio
import time

# Define segments for the 7-segment displays
segments_display1 = {
    'A': digitalio.DigitalInOut(board.GP1),
    'B': digitalio.DigitalInOut(board.GP2),
    'C': digitalio.DigitalInOut(board.GP3),
    'D': digitalio.DigitalInOut(board.GP4),
    'E': digitalio.DigitalInOut(board.GP5),
    'F': digitalio.DigitalInOut(board.GP6),
    'G': digitalio.DigitalInOut(board.GP7),
    'DP': digitalio.DigitalInOut(board.GP8)  # Optional decimal point pin
}

segments_display2 = {
    'A': digitalio.DigitalInOut(board.GP9),
    'B': digitalio.DigitalInOut(board.GP10),
    'C': digitalio.DigitalInOut(board.GP11),
    'D': digitalio.DigitalInOut(board.GP12),
    'E': digitalio.DigitalInOut(board.GP13),
    'F': digitalio.DigitalInOut(board.GP14),
    'G': digitalio.DigitalInOut(board.GP15),
    'DP': digitalio.DigitalInOut(board.GP16)  # Optional decimal point pin
}

# Set all segment pins to output mode
for segment in segments_display1.values():
    segment.direction = digitalio.Direction.OUTPUT

for segment in segments_display2.values():
    segment.direction = digitalio.Direction.OUTPUT

# Define patterns for digits (common cathode configuration)
patterns = {
    0: {'A': True, 'B': True, 'C': True, 'D': True, 'E': True, 'F': True, 'G': False, 'DP': False},
    1: {'A': False, 'B': True, 'C': True, 'D': False, 'E': False, 'F': False, 'G': False, 'DP': False},
    2: {'A': True, 'B': True, 'C': False, 'D': True, 'E': True, 'F': False, 'G': True, 'DP': False},
    3: {'A': True, 'B': True, 'C': True, 'D': True, 'E': False, 'F': False, 'G': True, 'DP': False},
    4: {'A': False, 'B': True, 'C': True, 'D': False, 'E': False, 'F': True, 'G': True, 'DP': False},
    5: {'A': True, 'B': False, 'C': True, 'D': True, 'E': False, 'F': True, 'G': True, 'DP': False},
    6: {'A': True, 'B': False, 'C': True, 'D': True, 'E': True, 'F': True, 'G': True, 'DP': False},
    7: {'A': True, 'B': True, 'C': True, 'D': False, 'E': False, 'F': False, 'G': False, 'DP': False},
    8: {'A': True, 'B': True, 'C': True, 'D': True, 'E': True, 'F': True, 'G': True, 'DP': False},
    9: {'A': True, 'B': True, 'C': True, 'D': True, 'E': False, 'F': True, 'G': True, 'DP': False}
}

def display_digit(display_index, digit):
    # Choose the segment dictionary based on the display index
    if display_index == 0:
        segments = segments_display1
    elif display_index == 1:
        segments = segments_display2
    else:
        raise ValueError("Invalid display index")

    # Set the segment pattern for the digit
    pattern = patterns.get(digit, {segment: False for segment in segments})
    for segment, state in pattern.items():
        segments[segment].value = state

def display_number(number):
    if 1 <= number <= 99:
        tens = number // 10
        units = number % 10
        display_digit(0, tens)  # Display tens digit on the first display
        display_digit(1, units)  # Display units digit on the second display

# Shock sensor setup
shock_sensor = digitalio.DigitalInOut(board.GP26)  # Change to your actual pin
shock_sensor.direction = digitalio.Direction.INPUT
shock_sensor.pull = digitalio.Pull.UP  # Pull-up resistor

# Initial counter value
counter = 1
last_sensor_state = True  # Assume sensor is not triggered initially

while True:
    current_sensor_state = shock_sensor.value
    
    # Check for transition from not triggered to triggered
    if not current_sensor_state and last_sensor_state:
        # Shock sensor has been triggered
        display_number(counter)
        counter = (counter % 99) + 1  # Increment counter and wrap around to 1 after 99
        time.sleep(0.5)  # Debounce delay to avoid multiple counts for a single trigger
    
    # Update last_sensor_state
    last_sensor_state = current_sensor_state
    
    time.sleep(0.1)  # Short delay to avoid busy-waiting


