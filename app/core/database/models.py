from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=False
    )
    username: Mapped[str] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    cars: Mapped[list['Car']] = relationship(
        'Car',
        back_populates='owner',
        cascade='all, delete-orphan'
    )


class Car(Base):
    __tablename__ = 'user_cars'
    __table_args__ = (
        UniqueConstraint('telegram_id', 'car_name', name='uq_user_car_name'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    car_name: Mapped[str] = mapped_column(String(100))

    telegram_id: Mapped[int] = mapped_column(
        ForeignKey('users.telegram_id')
    )
    owner: Mapped['User'] = relationship('User', back_populates='cars')
    repair_notes: Mapped[list['RepairHistory']] = relationship(
        'RepairHistory',
        back_populates='car',
        cascade='all, delete-orphan'
    )


class RepairHistory(Base):
    __tablename__ = 'car_repair_histories'

    id: Mapped[int] = mapped_column(primary_key=True)
    repair_date: Mapped[date] = mapped_column(Date, default=date.today)
    repair_description: Mapped[str] = mapped_column(String(500))
    mileage: Mapped[int] = mapped_column()

    car_id: Mapped[int] = mapped_column(
        ForeignKey('user_cars.id')
    )
    car: Mapped['Car'] = relationship('Car', back_populates='repair_notes')
