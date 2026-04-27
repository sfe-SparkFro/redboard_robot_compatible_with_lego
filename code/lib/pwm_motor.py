

from machine import Pin, PWM

class PWMMotor:
    def __init__(self, pwm_pin, dir_pin, reverse=False):
        self.pwm = PWM(Pin(pwm_pin))
        self.dir = Pin(dir_pin, Pin.OUT)
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)
        self.dir.value(0)
        self.reverse = reverse

    def set_speed(self, speed):
        self.pwm.duty_u16(int(abs(speed) * 65535))
        self.dir.value(not self.reverse if speed > 0 else self.reverse)
