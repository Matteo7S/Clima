#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from models import init, Measures, PumpStates
from config import Config

engine = create_engine('sqlite:///'+Config['dbfile'], echo=True)

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

# if __name__ == "__main__":
#     a = DB()
#     for i in range(1,5):
#         a.insert_measure(i, i+30)