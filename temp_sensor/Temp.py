import time
from datetime import datetime, timedelta
import threading
from w1thermsensor import W1ThermSensor
from tinydb import TinyDB, Query

class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()
        self.cur_temp = 999
        self.cur_time = datetime.now().replace(microsecond=0)
        self.min_temp = 999
        self.min_time = datetime.now().replace(microsecond=0)
        self.max_temp = 999
        self.max_time = datetime.now().replace(microsecond=0)
        self.db = TinyDB('./db/db.json')

    def get_temp(self):
        self.cur_temp = self.sensor.get_temperature()
        self.cur_time = datetime.now().replace(microsecond=0)

    def check_temp(self):
        if self.min_temp == 999:
            self.min_temp = self.cur_temp
        if self.max_temp == 999:
            self.max_temp = self.cur_temp
        if self.cur_temp < self.min_temp:
            self.min_temp = self.cur_temp
            self.min_time = self.cur_time
        if self.cur_temp > self.max_temp:
            self.max_temp = self.cur_temp
            self.max_time = self.cur_time

        max_temp_t_delta = self.cur_time - self.max_time
        min_temp_t_delta = self.cur_time - self.min_time
        day_t_delta = timedelta(hours=24)

        if max_temp_t_delta > day_t_delta:
            self.max_temp = self.cur_temp
            self.max_time = self.cur_time
        if min_temp_t_delta > day_t_delta:
            self.min_temp = self.cur_temp
            self.min_time = self.cur_time

    def store_temp(self):
        self.db.insert({'temp': self.cur_temp, 'time': self.cur_time.isoformat()})
            

    def fetch_temp(self):
        res = { 'temp': self.cur_temp, 'minTemp': {'temp': self.min_temp, 'time': self.min_time.isoformat()}, 'maxTemp': {'temp': self.max_temp, 'time': self.max_time.isoformat()}, 'time': self.cur_time.isoformat()}
        return res
    
    def tracking_loop(self):
        while True:
            self.get_temp()
            self.check_temp()
            self.store_temp()
            time.sleep(1)

    def start_temp_tracking(self):
        tracking_thread = threading.Thread(target=self.tracking_loop)
        tracking_thread.start()