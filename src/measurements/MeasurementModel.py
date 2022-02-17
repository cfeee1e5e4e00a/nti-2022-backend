from db import db
from sqlalchemy import Column, String, PickleType, Float
from sqlalchemy.dialects.postgresql import TIMESTAMP


class MeasurementModel(db.Model):
    __tablename__ = 'measurements'

    time = Column(Float(), nullable=False)
    sensor = Column(String(), nullable=False)
    value = Column(PickleType(), nullable=False)

