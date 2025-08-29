from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    cars = relationship('Car',
                        back_populates='owner',
                        cascade='all, delete-orphan')


class Car(Base):
    __tablename__ = 'user_cars'

    id = Column(Integer, primary_key=True)
    car_name = Column(String)

    telegram_id = Column(Integer, ForeignKey('users.telegram_id'))
    owner = relationship('User', back_populates='cars')
    repair_notes = relationship('RepairHistory',
                                back_populates='car',
                                cascade='all, delete-orphan')


class RepairHistory(Base):
    __tablename__ = 'car_repair_histories'

    id = Column(Integer, primary_key=True)
    repair_date = Column(Date, default=date.today)
    repair_description = Column(String)
    mileage = Column(Integer)

    car_id = Column(Integer, ForeignKey('user_cars.id'))
    car = relationship('Car', back_populates='repair_notes')
