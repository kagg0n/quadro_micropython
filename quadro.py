#--------LIBRARIES--------
import machine
from machine import PWM,Pin



#--------VARIABLES AND PRESETS---------
wanted_pitching = # желаемый угол тангажа
pitching_difference = # допустимая разница между желаемым углом и действительным
pitching = 0 # тангаж

wanted_roll = # желаемый угол крена
roll_difference = # допустимая разница между желаемым и действительным углом
roll = 0 # крен

sharpness_index = 1 # кожффицент резкости смены оборотов двигателей при разнице в углах
kalman_filter = 0.001

left_upper = Pin() # номер пина ЛЕВОГО ВЕРХНЕГО двигателя
right_upper = Pin() # номер пина ПРАВОГО ВЕРХНЕГО двигателя

left_bottom = Pin() # номер пина ЛЕВОГО НИЖНЕГО двигателя
right_bottom = Pin() # номер пина ПРАВОГО НИЖНЕГО двигателя

pwm_lu = PWM(left_upper)
pwm_ru = PWM(right_upper)

pwm_lb = PWM(left_bottom)
pwm_rb = PWM(right_bottom)


#-------MAIN CODE-------------
def map_arduino(x, in_min, in_max, out_min, out_max): # для квадрокоптера get_acx/acy,-32678,32767,0,1000
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class mpu6050():
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        self.iic.stop()

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_acx(self):
        raw_ints = self.get_raw_values()
        acx = {}
        acx["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        return acx  # returned in range of Int16
        # -32768 to 32767
    def get_acy(self):
        raw_ints = self.get_raw_values()
        acy = {}
        acy["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        return acy  # returned in range of Int16
        # -32768 to 32767
    def get_acz(self):
        raw_ints = self.get_raw_values()
        acz = {}
        acz["AcZ"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        return acz  # returned in range of Int16
        # -32768 to 32767

while True:
    ax = get_acx()
    ay = get_acy()
    
    roll = kalman_filter*ax +(1-kalman_filter)*roll
    pitching = kalman_filter*ay +(1-kalman_filter)*pitching
    
    pwm_ax = map_arduino(roll,-32768,32767,0,1000)
    pwm_ay = map_arduino(pitching,-32768,32767,0,1000) 
    
    pwm_lu.frequency(round((500 + (pwm_ax * -1)) + (500 * (pwm_ay * -1))) * sharpness_index)
    pwm_ru.frequency(round((500 + (pwm_ax * 1)) + (500 * (pwm_ay * -1))) * sharpness_index)
    pwm_lb.frequency(round((500 + (pwm_ax * -1)) + (500 * (pwm_ay * 1))) * sharpness_index)
    pwm_rb.frequency(round((500 + (pwm_ax * 1)) + (500 * (pwm_ay * 1))) * sharpness_index)
    