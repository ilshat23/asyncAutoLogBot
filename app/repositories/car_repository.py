from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Car


class CarRepository:
    """Репозиторий для работы с моделью автомобиля."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_car(self, car_name: str, user_id: int):
        car = Car(
            car_name=car_name,
            telegram_id=user_id
        )
        self.session.add(car)

    async def get_car_by_id(self, car_id: int) -> Car | None:
        car = await self.session.get(Car, car_id)
        return car

    async def get_car_by_name(self, car_name: str, user_id: int) -> Car | None:
        car = await self.session.scalar(
            select(Car).filter(
                Car.telegram_id == user_id,
                Car.car_name == car_name
            )
        )
        return car

    async def delete_car(self, car: Car) -> None:
        await self.session.delete(car)

    async def get_user_cars(self, user_id: int) -> Sequence[Car]:
        stmt = select(Car).filter(Car.telegram_id == user_id)
        res = await self.session.scalars(stmt)
        return res.all()

    async def rename_car(self, car: Car, car_name: str):
        car.car_name = car_name
