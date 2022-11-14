#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, inspect
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, Text, String, DateTime
from sqlalchemy.orm import relationship
from config import Config
import datetime
from sqlalchemy.ext.declarative import as_declarative
# engine = create_engine('sqlite:///'+Config['dbfile']) #echo=True
engine = create_engine('sqlite:///'+Config['dbfile_path']+Config['dbfile']+'?check_same_thread=False') #echo=True
# Base = declarative_base()
@as_declarative()
class Base:
    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return "User {}".format(self.name)

class Sensors(Base):
    __tablename__ = 'sensors'

    id = Column(Integer, primary_key=True)
    cod = Column(String)
    description = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "User {}".format(self.name)

class Measures(Base):
    __tablename__ = 'measures'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(String, ForeignKey("sensors.id"))  
    measure = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


    # def __repr__(self):
    #     return "".format(self.sensor_id, self.measure, self.time_created)
    

class Pumps(Base):
    __tablename__ = 'pumps'

    id = Column(Integer, primary_key=True)
    cod = Column(String)
    description = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # def __repr__(self):
    #     return "Pumps {}".format(self.description)

class PumpStates(Base):
    __tablename__ = 'pump_states'

    id = Column(Integer, primary_key=True)
    pump_id = Column(String, ForeignKey("pumps.id"))  
    state = Column(Integer)
    reason = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # def __repr__(self):
    #     return "PumpState {}".format(self.state)

class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    error = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


def init():
    Base.metadata.create_all(engine)