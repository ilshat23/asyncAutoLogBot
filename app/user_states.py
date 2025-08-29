from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import update

from app.cache import cached_data
from app.database.db import async_session
from app.database.models import Car, RepairHistory
from app.keyboards import car_delete_kb


state_router = Router()


class CarReg(StatesGroup):
    name = State()


class RepairInfoReg(StatesGroup):
    mileage = State()
    desc = State()


class RenameState(StatesGroup):
    name = State()


class CarDelete(StatesGroup):
    confirmation = State()


@state_router.message(CarReg.name)
async def set_car_name(message: Message,
                       state: FSMContext):
    new_car = message.text.strip()
    if new_car.startswith('/'):
        await message.reply('Название не может начинаться с /')
    else:
        car = Car(
            car_name=new_car,
            telegram_id=cached_data.get('user_id')
        )
        async with async_session() as session:
            session.add(car)
            await session.commit()
        await state.clear()
        await message.answer(f'{cached_data.get('first_name')}, '
                             f'твой автомобиль {new_car} успешно сохранен!')
        cached_data.clear()


@state_router.message(RepairInfoReg.mileage)
async def set_mileage(message: Message, state: FSMContext):
    mileage = message.text.strip(' км.km')

    if not mileage.isdigit():
        await message.answer('Введи только числовое обозначение пробега.')
    elif mileage.startswith('/'):
        await message.answer('Пробег не может начинаться с /')
    else:
        await state.update_data(mileage=int(mileage))
        await state.set_state(RepairInfoReg.desc)
        await message.answer('Отлично! Теперь напиши, что было проделано.')


@state_router.message(RepairInfoReg.desc)
async def set_desc(message: Message, state: FSMContext):
    desc = message.text.strip()
    data = await state.get_data()
    async with async_session() as session:
        repair_note = RepairHistory(
            repair_description=desc,
            mileage=data.get('mileage'),
            car_id=cached_data[message.from_user.id].get('selected_car_id')
        )
        session.add(repair_note)
        await session.commit()
        await state.clear()
    await message.reply('Запись добавлена!')


@state_router.message(CarDelete.confirmation)
async def delete_car(message: Message, state: FSMContext):
    await message.answer('Можно и отменить свой выбор',
                         reply_markup=car_delete_kb)


@state_router.message(RenameState.name)
async def rename_car(message: Message, state: FSMContext):
    new_name = message.text.strip()
    if new_name.startswith('/'):
        await message.reply('Название не может начинаться с <b>/</b>',
                            parse_mode='Html')
    else:
        car_id = cached_data[message.from_user.id].get('selected_car_id')
        async with async_session() as session:
            await session.execute(
                update(Car).where(Car.id == car_id).values(car_name=new_name)
            )
            await session.commit()
            await message.answer(f'Название <b>{new_name}</b> сохранено.',
                                 parse_mode='Html')
            cached_data.clear()
            await state.clear()
