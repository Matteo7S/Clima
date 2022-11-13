#!/usr/bin/env python3
# import numpy as np
from numpy import diff
from statistics import mean
from datetime import datetime, timedelta
import random
import time
import traceback
from time import sleep
# import RPi.GPIO as GPIO

from w1thermsensor import W1ThermSensor, Sensor
import max6675
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setwarnings(True)

from config import Config
from database import DB
from log import Log



db = DB()
log = Log()

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
                sleep(5)
            except Exception as err:
                log.log("Error running Tools MeasureTools thread", error=err)
            
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
        max6675.set_pin(cs, sck, so, 1)
    
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
            except Exception as err:
                log.log("Error performing MAXX6675 measure", error=err)
        else:
            try:
                temp = self.get_measure_1_Wire(id)
            except Exception as err:
                log.log("Error performing 1_Wire measure", error=err)
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
                log.log("Error sampling MAXX6675", error=err)
        
        

    def get_measure_value_1_Wire(self, sensor_cod):
        # temp = await W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_cod).get_temperature()
        try:
            temp = W1ThermSensor(Sensor.DS18B20, sensor_cod).get_temperature()
            return temp
        except Exception as err:
                log.log("Error sampling W1ThermSensor", error=err)

class Camino:
    def __init__(self):
        self.sensors = Sensors()
        self.measureTools = MeasureTools()
        self.pump_state = 0
        self.pump_id = 1

    def trend(self):
        t_cappa_array = [46,45,46] #db.get_last_t_cappa(self)
        d_t_cappa_array = diff(t_cappa_array)
        n_of_measures = d_t_cappa_array.size
        x = sum(1 for i in d_t_cappa_array if i >= 0 )
        n_of_neg = n_of_measures-x
        if n_of_neg == n_of_measures:
            return 0
        else:
            return 1 

    def check_state(self):
        try:
            t_camino = db.get_measure(1)
            t_in = db.get_measure(4)
            t_out = db.get_measure(3)
            t_boiler = db.get_measure(2)

            if t_camino.measure >= Config["tMax"]:
                self.pump_state = 1
                db.insert_state(self.pump_id, 1, "t_camino >= tMax")
                return
            elif t_camino.measure >= Config["tStart"]:
                if self.trend():
                    self.pump_state = 1
                    db.insert_state(self.pump_id, 1, "trend temp. cappa in crescita")
                    return
                else:
                    if t_in.measure > t_out.measure:
                        self.pump_state = 0
                        db.insert_state(self.pump_id, 0, "t_in > t_out")
                        return
                    elif t_boiler.measure > t_out.measure:
                        self.pump_state = 0
                        db.insert_state(self.pump_id, 0, "t_boiler > t_out")
                        return
                    else:
                        self.pump_state = 1
                        db.insert_state(self.pump_id, 1, "t_out >")
                        return
            else: 
                self.pump_state = 0
                db.insert_state(self.pump_id, 0, "t_camino < tStart")
                return
        except Exception as err:
                log.log("Error get temp from db", error=err)

#Pumps
class Pumps:
    def __init__(self):
        print('figa')
    
    def trigger_pins_off(self, delay=1):
        GPIO.output(32, GPIO.HIGH)
        time.sleep(delay)
    
    def trigger_pins_on(self, delay=1):
        GPIO.output(32, GPIO.LOW)
        time.sleep(delay)
    
    def turnOn(self, pump_id):
        try:
            self.trigger_pins_on()
        except Exception as err:
            # log.log("Error trigger pump pin LOW", error=err)
            pass

    def turnOff(self, pump_id):
        try: 
            self.trigger_pins_off()
        except Exception as err:
            # log.log("Error trigger pump pin HIGH", error=err)
            pass
    
    def get_pumps_state(self):
        pumps_state = []
        try:
            a={}
            pumps_list = db.get_pumps()
            for pump in pumps_list:
                state = db.get_pump_state(pump.id)
                if state == None:
                    st = 0
                else:
                    st = state.state
                a = {"id":pump.id, "state":st}
                pumps_state.append(a)
            return pumps_state
            
        except Exception as err:
            log.log("Error trigger pump pin HIGH", error=err)
    
    def pump_manager(self):
        pumps_state = self.get_pumps_state()
        for i in pumps_state:
            if i["state"] == 1:
                self.turnOn(i["id"])
            else:
                self.turnOff(i["id"])
    
    


# if __name__ == "__main__":
#     a = Pumps()
#     a.turnOff(1)
#     sleep(2)
#     a.turnOn(1)
    