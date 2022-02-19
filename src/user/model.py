from dataclasses import dataclass
from db import db
from sqlalchemy import Column, Integer, String, Float, PickleType, ForeignKey, BIGINT
from sqlalchemy.orm import relationship





class ProfileModel(db.Model):
    __tablename__ = "profiles"

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    surname = Column(String())
    age = Column(Integer())
    sex = Column(String())


class MedCardModel(db.Model):
    __tablename__ = 'cards'

    id = Column(Integer(), primary_key=True)
    weight = Column(Float())
    assignments = Column(PickleType())


class UserModel(db.Model):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    login = Column(String(), nullable=False, unique=True)
    # TODO: store passwords securely
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    rfid = Column(BIGINT())
    face = Column(Integer())

    profile_id = Column(Integer(), ForeignKey('profiles.id'))
    profile: ProfileModel = relationship("ProfileModel")

    card_id = Column(Integer(), ForeignKey('cards.id'))
    card: MedCardModel = relationship("MedCardModel")

