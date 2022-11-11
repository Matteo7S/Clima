#!/usr/bin/env python3
import os
import json

app_path = os.path.dirname(os.path.realpath(__file__))
Config = None
try:
    cfg_path = os.path.join(app_path, "config.json")
    with open(cfg_path, 'r') as f:
        Config = json.load(f)

except Exception:
    pass

if not isinstance(Config, dict):
    Config = {}

Config["app_path"] = app_path
del app_path

if "dbfile" not in Config:
    Config["dbfile"] = "home.db"

if "host" not in Config:
    Config["host"] = "0.0.0.0"

if "port" not in Config:
    Config["port"] = 65432

if "debug" not in Config:
    Config["debug"] = False

if "secret" not in Config:
    Config["secret"] = "ChangeMeNow"

if "title" not in Config:
    Config["title"] = "Camino System"

if "pidfile" not in Config:
    Config["pidfile"] = "/var/run/sensorsystem.pid"

if "pidfile" not in Config:
    Config["pidfile_camino"] = "/var/run/caminosystem.pid"

if "manager_sleep" not in Config:
    Config["manager_sleep"] = 10

if "sensor_reader_sampling_time" not in Config:
    Config["sensor_reader_sampling_time"] = 60

if "auto_start" not in Config:
    Config["auto_start"] = 1

if "auto_arm" not in Config:
    Config["auto_arm"] = 1

# Camino manager

if "camino_check_time" not in Config:
    Config["camino_check_time"] = 1

if "sensor_camino" not in Config:
    Config["sensor_camino"] = "Camino"

if "sensor_camino_in" not in Config:
    Config["sensor_camino_in"] = "CaminoIn"

if "sensor_camino_out" not in Config:
    Config["sensor_camino_out"] = "CaminoOut"

if "cappa" not in Config:
    Config["Cappa"] = "Cappa"

if "tMax" not in Config:
    Config["tMax"] = 70

if "tStart" not in Config:
    Config["tStart"] = 45

if "tStartToll" not in Config:
    Config["tStartToll"] = 6

#Numero di riferimenti per il calcolo della derivata
if "numObs" not in Config:
    Config["numObs"] = 7



    
