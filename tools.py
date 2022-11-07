
# import numpy as np
from statistics import mean
from datetime import datetime, timedelta
import random
import time
import traceback
from time import sleep
import RPi.GPIO as GPIO

from w1thermsensor import W1ThermSensor, Sensor
import max6675
# import RPi.GPIO as GPIO
# from w1thermsensor import W1ThermSensor
from config import Config
from database import DB

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setwarnings(False)

db = DB()

# set the pin for communicate with MAX6675
cs = 24
sck = 23
so = 21

class MeasureTools:
    def __init__(self):
        self.sensors = Sensors()

    def measurator(self):
        temp = 0
        for i in self.sensors.sensors_list:
            try:
                temp = self.get_measure(i["id"])
                db.insert_measure(i["id"], temp)
                sleep(Config["sensor_reader_sampling_time"])
            except Exception as err:
                self.log("Error running Tools MeasureTools thread", error=err)
            
            # print(i["id"])
            # print(temp)

    def get_measure(self, sensor_id):
        ms = self.perform_measure(sensor_id)
        ms = self.clean_measure(ms)
        measure = mean(ms)
        return round(measure, 1)

    def perform_measure(self, sensor_id):
        measure_array = []
        for i in range(5):
            measure = self.sensors.get_measure(sensor_id)
            measure_array.append(measure)
        return measure_array

    def clean_measure(self, measure_array):
        measure_array.sort()
        measure_array = measure_array[1:]
        measure_array = measure_array[:-1]
        return measure_array

    def integrity_check(self, date):
        present = datetime.now()
        return datetime.strptime(date) + timedelta(minutes=5) > present

    def log(self, message, error=None):
        timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        if error:
            trace = traceback.format_exc()
            message += "\n" + trace
        message = timestamp + " " + message
        print(message)

class Sensors:
    def __init__(self):
        self.sensors_list = [
            {"id":1, "cod": "0315a1e359ff", "description": "Camino"},
            {"id":2, "cod": "0415a1c94fff", "description": "Boiler"},
            {"id":3, "cod": "0417002fa9ff", "description": "CaminoOut"},
            {"id":4, "cod": "0316a7a8deff", "description": "CaminoIn"},
            {"id":5, "cod": "", "description": "Cappa"}
            #manca la sonda della cappa
        ]
    
    def find_cod_from_id(self, id):
        s = next(item for item in self.sensors_list if item["id"] == id)
        return s['cod']

    def get_sensor_from_id(self, id):
        for sensor in self.sensors_list:
            if sensor["id"] == id:
                return sensor["cod"]
    
    def get_sensor_from_description(self, description):
        for sensor in self.sensors_list:
            if sensor["description"] == description:
                return sensor["cod"]

    def get_measure(self, id):
        if id == 5:
            try:
                temp = self.get_measure_MAXX6675(id)
            except KeyError:
                return False
        else:
            try:
                temp = self.get_measure_1_Wire(id)
            except KeyError:
                return False
        return temp

    def get_measure_1_Wire(self,id):
        # cod = self.get_sensor_from_id(id)
        cod = self.find_cod_from_id(id)
        temp = self.get_measure_value_1_Wire(cod)
        # print("1wire: ")
        # print(temp)
        return temp

    def get_measure_MAXX6675(self,id):
        cod = 1
        temp = self.get_measure_value_MAXX6675(cod)
        # print("MAXX6675: ")
        # print(temp)
        return temp

    def get_measure_value_MAXX6675(self, sensor_cod):
        # temp = await W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_cod).get_temperature()
        try:
            # read temperature connected at CS 22
            temp = max6675.read_temp(cs)
            return temp
        except Exception as err:
                self.log("Error sampling MAXX6675", error=err)
        
        

    def get_measure_value_1_Wire(self, sensor_cod):
        # temp = await W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_cod).get_temperature()
        try:
            temp = W1ThermSensor(Sensor.DS18B20, sensor_cod).get_temperature()
            return temp
        except Exception as err:
                self.log("Error sampling W1ThermSensor", error=err)

    def log(self, message, error=None):
        timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        if error:
            trace = traceback.format_exc()
            message += "\n" + trace
        message = timestamp + " " + message
        print(message)

class Camino:
    def __init__(self):
        self.sensors = Sensors()


if __name__ == "__main__":
    a = MeasureTools()
    a.measurator()