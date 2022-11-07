from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, Text, String, DateTime

engine = create_engine('sqlite:///camino_db', echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return f'User {self.name}'


class Measures(Base):
    __tablename__ = 'measures'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(String)
    measure = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'User {self.name}'

def init():
    Base.metadata.create_all(engine)