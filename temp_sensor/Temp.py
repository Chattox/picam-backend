import time
from w1thermsensor import W1ThermSensor

class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()

    def get_temp(self):
        temp_c = self.sensor.get_temperature()
        res = { 'temp': temp_c }
        return res