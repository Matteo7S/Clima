#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from models import init, Measures, PumpStates, Pumps, Log
from config import Config

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///'+Config['dbfile_path']+Config['dbfile']) #echo=True

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

class DB:
    def __init__(self):
        init()

    def ciao(self):
        print('ciaone')

    def insert_measure(self, sensor_id, measure):
        session = Session()
        measure = Measures(
            sensor_id = sensor_id,
            measure = measure
        )
        session.add(measure)  # Add the measure
        session.commit()  # Commit the change
        session.close()
        Session.remove()
        return

    def get_measure(self, sensor_id):
        session = Session()
        measure = session.query(Measures).filter_by(sensor_id=sensor_id).order_by(Measures.id.desc()).first()
        session.close()
        Session.remove()
        return measure
    
    def get_last5(self, sensor_id):
        session = Session()
        measure = session.query(Measures).filter_by(sensor_id=sensor_id).order_by(Measures.id.desc()).limit(5)
        session.close()
        Session.remove()
        return measure

    def insert_state(self, pump_id, state, reason):
        session = Session()
        pump_states = PumpStates(
            pump_id = pump_id,
            state = state,
            reason = reason
        )
        session.add(pump_states)  # Add the measure
        session.commit()  # Commit the change
        session.close()
        Session.remove()
        return


    def get_pump_state(self, pump_id):
        session = Session()

        state = session.query(PumpStates).filter_by(pump_id=pump_id).order_by(PumpStates.id.desc()).first()
        session.close()
        Session.remove()

        return state
    
    def get_pumps(self):
        session = Session()

        pumps = []
        pumps = session.query(Pumps).all()
        session.close()
        Session.remove()

        return pumps
    
    def insert_log(self, message,error):
        session = Session()

        log = Log(
            message = message,
            error = error
        )
        session.add(log)  
        session.commit()  
        session.close()
        Session.remove()
        return

if __name__ == "__main__":
    a = DB()
    try:
        log = a.get_last5(1)
        print(log)
    except Exception as err:
        print("errore ")
        print("err")
