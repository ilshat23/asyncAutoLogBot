from datetime import datetime as dt
from typing import List

from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.cache import cached_data
from app.database.db import async_session
from app.database.models import Car
from telegram_client import TelegramClient


async def get_car(car_id: int) -> tuple[Car, AsyncSession]:
    async with async_session() as session:
        result = await session.get(Car, car_id)
        if result is None:
            raise TypeError('Объект не может быть None')
        return result, session


async def delete_car(car_id: int):
    car, session = await get_car(car_id)
    await session.delete(car)
    await session.commit()


async def get_all_cars(user_id: int) -> List[Car]:
    async with async_session() as session:
        result = await session.execute(
            select(Car).where(Car.telegram_id == user_id)
        )
        return list(result.scalars().all())


# async def handle_one_or_many_cars(
#     message: Message,
#     cars: List[Car],
#     state: FSMContext,
#     state_status_if_one: State,
#     text_if_one_car: str = '',
#     text_if_many_cars: str = '',
#     cmd: str = '',
#     state_status_if_many: State | None = None
# ) -> None:
#     if not cars:
#         message.answer('У тебя нет автомобилей в коллекции.')
#     else:
#         if len(cars) < 2:
#             await state.set_state(state_status_if_one)
#             cached_data['car_id'] = cars[0].id
#             await message.answer(text_if_one_car,
#                                  parse_mode='Html')
#         else:
#             await state.set_state(state_status_if_many)
#             await message.answer(text_if_many_cars,
#                                  reply_markup=await inline_cars(cars, cmd))


async def get_car_and_update_cache(callback: CallbackQuery) -> str:
    user_id = callback.from_user.id
    car_name = cached_data[user_id].get('selected_car')
    car_id = cached_data[user_id].get(car_name)
    cached_data[user_id]['selected_car_id'] = car_id
    return car_name


async def send_err_msg(tg: TelegramClient,
                       err: Exception,
                       admin: str | None = None):

    msg = (f'{dt.now().strftime("%Y/%m/%d %H:%M")} --- '
           f'{err.__class__} --- {err}')

    await tg.post('sendMessage',
                  params={'text': msg,
                          'chat_id': admin})
