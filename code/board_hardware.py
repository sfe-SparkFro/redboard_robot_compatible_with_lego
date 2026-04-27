from lib.pwm_motor import PWMMotor
from lib.lego_devices.color_sensor import ColorSensor

# Create color sensor
color_sensor = ColorSensor(tx=32, rx=33)

# Create the motors
motor_l = PWMMotor(pwm_pin=29, dir_pin=28, reverse=True)
motor_r = PWMMotor(pwm_pin=31, dir_pin=30)
