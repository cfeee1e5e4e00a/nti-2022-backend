from dataclasses import dataclass
from db import db
from sqlalchemy import Column, Integer, String


class UserModel(db.Model):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    login = Column(String(), nullable=False, unique=True)
    # TODO: store passwords securely
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
