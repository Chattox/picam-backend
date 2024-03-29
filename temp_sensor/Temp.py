import time
from datetime import datetime, timedelta
import threading
from w1thermsensor import W1ThermSensor
from tinydb import TinyDB, Query
import statistics
import numpy as np
from math import floor

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
        self.TempQuery = Query()
        self.tracking_loop_interval_seconds = 5
        self.storage_loop_interval_seconds = 900

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
            time.sleep(self.tracking_loop_interval_seconds)

    def storage_loop(self):
        while True:
            self.get_temp()
            self.store_temp()
            time.sleep(self.storage_loop_interval_seconds)

    def start_temp_tracking(self):
        tracking_thread = threading.Thread(target=self.tracking_loop)
        tracking_thread.start()

    def start_temp_storing(self):
        storage_thread = threading.Thread(target=self.storage_loop)
        storage_thread.start()

    def get_full_temp_history(self):
        return self.db.all()
    
    def get_day_temp_history(self):
        now = datetime.now().replace(microsecond=0)
        day_t_delta = timedelta(hours=24)
        
        return self.db.search(self.TempQuery.time.test(self.within_timeframe, now, day_t_delta))
    
    def get_week_temp_history(self):
        now = datetime.now().replace(microsecond=0)
        week_t_delta = timedelta(days=7)

        temp_history = self.db.search(self.TempQuery.time.test(self.within_timeframe, now, week_t_delta))
        return self.__get_temp_averages(now, "week", temp_history)
    
    def get_month_temp_history(self):
        now = datetime.now().replace(microsecond=0)
        month_t_delta = timedelta(days=30)

        temp_history = self.db.search(self.TempQuery.time.test(self.within_timeframe, now, month_t_delta))
        return self.__get_temp_averages(now, "month", temp_history)
    
    def get_all_temp_history(self):
        now = datetime.now().replace(microsecond=0)
        temp_history = self.db.all()
        return self.__get_temp_averages(now, "all", temp_history)
    
    def get_collated_temp_history(self):
        return {'day': self.get_day_temp_history(), 'week': self.get_week_temp_history(), 'month': self.get_month_temp_history(), 'all': self.get_all_temp_history()}
    
    def within_timeframe(self, time, target_time, timeframe):
        temp_delta = target_time - datetime.fromisoformat(time)
        return temp_delta < timeframe
    
    def __get_temp_averages(self, now, timescale, data):
        current = now
        result = []
        segment = []
        t_delta = timedelta(hours=0)

        if (timescale == "week"):
            t_delta = timedelta(hours=2)
        elif (timescale == "month"):
            t_delta = timedelta(hours=8)
        elif (timescale == "all"):
            data_segments = np.array_split(data, 100)
            for i in data_segments:
                for j in i:
                    segment.append(j['temp'])
                result.append({'temp': statistics.mean(segment), 'time': i[0]['time']})
                segment = []

            return result
 
        for i in reversed(data):
                if (self.within_timeframe(i['time'], current, t_delta)):
                    segment.append(i['temp'])
                else:
                    result.append({'temp': statistics.mean(segment), 'time': current.isoformat() })
                    current = current - t_delta
                    segment = []
                    segment.append(i['temp'])
                    
        result.reverse()            
        return result