
import sys
# setting path
sys.path.append('/Users/Matteo/Sviluppo/github/Clima')
from database import DB
from flask import Blueprint
from flask import Flask, render_template
from flask import jsonify

db = DB()

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
        'id':t_camino.id,
        'data':t_camino.time_created,
        'measure':t_camino.measure
    }
    resp.append(camino)

    cappa = {
        'id':t_cappa.id,
        'measure':t_cappa.measure
    }
    resp.append(cappa)

    tin = {
        'id':t_in.id,
        'data':t_in.time_created,
        'measure':t_in.measure
    }
    resp.append(tin)

    tout = {
        'id':t_out.id,
        'data':t_out.time_created,
        'measure':t_out.measure
    }
    resp.append(tout)

    boiler = {
        'id':t_boiler.id,
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
        'state':state.state
    }

    return jsonify(resp)