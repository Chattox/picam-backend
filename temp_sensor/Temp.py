import time
import threading
from w1thermsensor import W1ThermSensor

class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()
        self.cur_temp = 999
        self.min_temp = 999
        self.min_time = time.time() * 1000
        self.max_temp = 999
        self.max_time = time.time() * 1000

    def get_temp(self):
        self.cur_temp = self.sensor.get_temperature()
        if self.min_temp == 999:
            self.min_temp = self.cur_temp
        if self.max_temp == 999:
            self.max_temp = self.cur_temp
        if self.cur_temp < self.min_temp:
            self.min_temp = self.cur_temp
            self.min_time = time.time() * 1000
        if self.cur_temp > self.max_temp:
            self.max_temp = self.cur_temp
            self.max_time = time.time() * 1000

    def fetch_temp(self):
        res = { 'temp': self.cur_temp, 'minTemp': {'temp': self.min_temp, 'time': self.min_time}, 'maxTemp': {'temp': self.max_temp, 'time': self.max_time}, 'time': time.time() * 1000 }
        return res
    
    def tracking_loop(self):
        while True:
            self.get_temp()
            time.sleep(1)

    def start_temp_tracking(self):
        tracking_thread = threading.Thread(target=self.tracking_loop)
        tracking_thread.start()