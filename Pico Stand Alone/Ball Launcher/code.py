"""
DESCRIPTION:
This example code will launch the ball
with dual DC motor using ROBO Pico with PICO 

AUTHOR   : Cytron Technologies Sdn Bhd
WEBSITE  : www.cytron.io
EMAIL    : support@cytron.io

"""
import time
import board
import digitalio
import pwmio
from adafruit_motor import motor
from analogio import AnalogIn
import adafruit_motor.servo

# Motor pins
PWM_MOTOR_A1 = board.GP8
PWM_MOTOR_B1 = board.GP9
PWM_MOTOR_A2 = board.GP10
PWM_MOTOR_B2 = board.GP11

# Button pin
BUTTON_ON_OFF = board.GP21

# Potentiometer pin
POTENTIOMETER_PIN = board.GP28

# Servo pin
SERVO_PIN = board.GP15

# Setup motors
pwm_a1 = pwmio.PWMOut(PWM_MOTOR_A1, frequency=10000)
pwm_b1 = pwmio.PWMOut(PWM_MOTOR_B1, frequency=10000)
motor1 = motor.DCMotor(pwm_a1, pwm_b1)

pwm_a2 = pwmio.PWMOut(PWM_MOTOR_A2, frequency=10000)
pwm_b2 = pwmio.PWMOut(PWM_MOTOR_B2, frequency=10000)
motor2 = motor.DCMotor(pwm_a2, pwm_b2)

# Setup button
button_on_off = digitalio.DigitalInOut(BUTTON_ON_OFF)
button_on_off.direction = digitalio.Direction.INPUT
button_on_off.pull = digitalio.Pull.UP

# Setup potentiometer
potentiometer = AnalogIn(POTENTIOMETER_PIN)

# Setup servo
servo_pwm = pwmio.PWMOut(SERVO_PIN, frequency=50)
servo = adafruit_motor.servo.Servo(servo_pwm)

def get_potentiometer_value():
    # Scale the potentiometer value from 0-65535 to 0-180 for servo angle
    return (potentiometer.value / 65535) * 180

motor_running = False
previous_button_state = True

while True:
    current_button_state = button_on_off.value

    # Detect button press (transition from high to low)
    if previous_button_state and not current_button_state:
        motor_running = not motor_running  # Toggle motor state
        print(f"Motor state toggled: {'ON' if motor_running else 'OFF'}")

    previous_button_state = current_button_state

    if motor_running:
        motor1.throttle = 1  # Full speed when motor is running
        motor2.throttle = 1  # Full speed when motor is running
    else:
        motor1.throttle = 0
        motor2.throttle = 0

    # Control servo with potentiometer
    servo_angle = get_potentiometer_value()
    print(f"Servo Angle: {servo_angle}")
    servo.angle = servo_angle

    time.sleep(0.1)
