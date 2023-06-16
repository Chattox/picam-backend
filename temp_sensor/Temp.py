import time
from w1thermsensor import W1ThermSensor

class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()
        self.min_temp = 999
        self.min_time = time.time() * 1000
        self.max_temp = 999
        self.max_time = time.time() * 1000

    def get_temp(self):
        temp_c = self.sensor.get_temperature()
        if self.min_temp == 999:
            self.min_temp = temp_c
        if self.max_temp == 999:
            self.max_temp = temp_c
        if temp_c < self.min_temp:
            self.min_temp = temp_c
            self.min_time = time.time() * 1000
        if temp_c > self.max_temp:
            self.max_temp = temp_c
            self.max_time = time.time() * 1000

        res = { 'temp': temp_c, 'minTemp': {'temp': self.min_temp, 'time': self.min_time}, 'maxTemp': {'temp': self.max_temp, 'time': self.max_time}, 'time': time.time() * 1000 }
        return res