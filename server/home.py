
import sys
# setting path
sys.path.append('/Users/Matteo/Sviluppo/github/Clima')
from database import DB
# from tools import Pumps
from log import Log
from flask import Blueprint
from flask import Flask, render_template
from flask import jsonify

db = DB()
log = Log()

home_bp = Blueprint('home', __name__)

@home_bp.route('/hello/')
def hello():
    return render_template('index.html')

@home_bp.route('/sensors/')
def sensors():
    t_camino = db.get_measure(1)
    t_in = db.get_measure(4)
    t_out = db.get_measure(3)
    t_boiler = db.get_measure(2)
    t_cappa = db.get_measure(5)

    resp = []

    camino = {
        'id':t_camino.sensor_id,
        'data':t_camino.time_created,
        'measure':t_camino.measure
    }
    resp.append(camino)

    cappa = {
        'id':t_cappa.sensor_id,
        'measure':t_cappa.measure
    }
    resp.append(cappa)

    tin = {
        'id':t_in.sensor_id,
        'data':t_in.time_created,
        'measure':t_in.measure
    }
    resp.append(tin)

    tout = {
        'id':t_out.sensor_id,
        'data':t_out.time_created,
        'measure':t_out.measure
    }
    resp.append(tout)

    boiler = {
        'id':t_boiler.sensor_id,
        'data':t_boiler.time_created,
        'measure':t_boiler.measure
    }
    
    resp.append(boiler)

    return jsonify(resp)

@home_bp.route('/states/')
def states():
    state = db.get_pump_state(1)

    resp = {
        'id':state.id,
        'data':state.time_created,
        'state':state.state,
        'reason':state.reason,
    }

    return jsonify(resp)

@home_bp.route('/caminoon/')
def caminoon():
    try:
        db.insert_state(self.pump_id, 1, "start by web")
        return jsonify(200)
    except Exception as err:
        log.log("Error trigger pump On from web", error=err)
        return jsonify(400)

@home_bp.route('/caminooff/')
def caminooff():
    try:
        db.insert_state(self.pump_id, 0, "stop by web")
        return jsonify(200)
    except Exception as err:
        log.log("Error trigger pump Off from web", error=err)
        return jsonify(400)