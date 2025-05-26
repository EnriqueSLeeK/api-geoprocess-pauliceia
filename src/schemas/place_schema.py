from sqlalchemy import Column, Integer, Float, String, Table
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class lugares_area_piloto2(Base):
    __tablename__ = 'places_pilot_area2'

    id = Column(Integer, primary_key=True, index=True)
    id_street = Column(Integer, nullable=True)
    number = Column(Integer, nullable=True)
    original_n = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    date = Column(String(255), nullable=True)
    first_day = Column(Integer, nullable=True)
    first_month = Column(Integer, nullable=True)
    first_year = Column(Integer, nullable=True)
    last_day = Column(Integer, nullable=True)
    last_month = Column(Integer, nullable=True)
    last_year = Column(Integer, nullable=True)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
