#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from models import init, Measures, PumpStates, Pumps, Log
from config import Config

engine = create_engine('sqlite:///'+Config['dbfile_path']+Config['dbfile']) #echo=True

Session = sessionmaker(bind=engine)
session = Session()

class DB:
    def __init__(self):
        init()

    def ciao(self):
        print('ciaone')

    def insert_measure(self, sensor_id, measure):
        measure = Measures(
            sensor_id = sensor_id,
            measure = measure
        )
        session.add(measure)  # Add the measure
        session.commit()  # Commit the change
        session.close()

    def get_measure(self, sensor_id):
        measure = session.query(Measures).filter_by(sensor_id=sensor_id).order_by(Measures.id.desc()).first()
        session.close()
        return measure

    def insert_state(self, pump_id, state, reason):
        pump_states = PumpStates(
            pump_id = pump_id,
            state = state,
            reason = reason
        )
        session.add(pump_states)  # Add the measure
        session.commit()  # Commit the change
        session.close()

    def get_pump_state(self, pump_id):
        state = session.query(PumpStates).filter_by(pump_id=pump_id).order_by(PumpStates.id.desc()).first()
        session.close()
        return state
    
    def get_pumps(self):
        pumps = []
        pumps = session.query(Pumps).all()
        session.close()
        return pumps
    
    def insert_log(self, message,error):
        log = Log(
            message = message,
            error = error
        )
        session.add(log)  
        session.commit()  
        session.close()

# if __name__ == "__main__":
#     a = DB()
#     try:
#         log = a.insert_log("ciuccia", "pina")
#     except Exception as err:
#         print("errore ")
#         print("err")
