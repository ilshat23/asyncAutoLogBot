from typing import Sequence

from core.cache import cached_data
from repositories.car_repository import CarRepository
from core.database.models import Car


class CarService:
    def __init__(self, car_repo: CarRepository) -> None:
        self.car_repo = car_repo

    async def get_cars(self, user_id: int) -> Sequence[Car]:
        cars = await self.car_repo.get_user_cars(user_id)
        return cars

    async def get_car(self, car_id: int) -> Car:
        car = await self.car_repo.get_car_by_id(car_id)
        return car

    async def get_car_or_id(
        self, car_name: str, user_id: int, instance_mode: bool = False
    ) -> int | Car:
        """
        Получить идентификатор автомобиля.

        Сначала ищет айди в кэше, если его там нет, то делает запрос к БД.
        Также сохраняет идентификатор автомобиля в кэше.

        Args:
            car_name (str): Наименование автомобиля.
            user_id (int): Идентификатор пользователя (его телеграм ид).
            instance_mode (bool): В этом режиме возвращается объект Car.

        Returns:
            int: Идентификатор автомобиля.
        """
        try:
            car_id = cached_data[user_id]['cars'][car_name]

            if instance_mode:
                car = await self.car_repo.get_car_by_id(car_id)

                if car is None:
                    raise ValueError('Такого автомобиля нет.')

                return car

            return car_id
        except KeyError:
            car = await self.car_repo.get_car_by_name(
                car_name=car_name,
                user_id=user_id
            )

            if car is None:
                raise ValueError('Такого автомобиля нет')

            if instance_mode:
                return car

            if user_id not in cached_data:
                cached_data[user_id] = {'cars': {}}

            cached_data[user_id]['cars'][car_name] = car.id

            return car.id

    async def create_car(self, car_name: str, user_id: int):
        await self.car_repo.create_car(car_name, user_id)

    async def delete_car(self, car: Car):
        await self.car_repo.delete_car(car)

    async def rename_car(self, car: Car, car_name: str):
        await self.car_repo.rename_car(car, car_name)
