# скетч для проверки оборотов двигателей


from machine import PWM,Pin
from time import sleep
n = 0
motor_pins = [3,5,7,9]
while True:
    for i in range(1000):
        pwm = PWM(motor_pins[n])
        pwm.freg(i)
        if i == 1000:
            n = n + 1
        if n == 3:
            n = 0
        
    