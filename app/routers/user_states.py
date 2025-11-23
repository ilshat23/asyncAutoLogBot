from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.cache import cached_data
from core.database.models import Car
from core.dependencies import (
    get_async_session, get_car_repository, get_car_service,
    get_repair_repository, get_repair_service
)
from core.exceptions import CarExistsError

from utils.keyboards import car_delete_kb


state_router = Router()


class CarReg(StatesGroup):
    name = State()


class RepairInfoReg(StatesGroup):
    mileage = State()
    desc = State()


class CarRename(StatesGroup):
    name = State()


class CarDelete(StatesGroup):
    confirmation = State()


@state_router.message(CarReg.name)
async def register_car(
    message: Message,
    state: FSMContext
):
    user_id = message.from_user.id
    new_car = message.text.strip()

    if new_car.startswith('/'):
        await message.reply('Название не может начинаться с /')
    else:
        async with get_async_session() as session:
            car_service = get_car_service(
                get_car_repository(session)
            )
            try:
                await car_service.create_car(
                    car_name=new_car,
                    user_id=user_id
                )
                await state.clear()
                await message.answer(
                    f'{message.from_user.first_name}, '
                    f'твой автомобиль {new_car} успешно сохранен!'
                )
                cached_data.pop(user_id, None)
            except CarExistsError as err:
                await message.reply(
                    f'{str(err)} <b>{new_car}</b>',
                    parse_mode='HTML'
                )


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
    async with get_async_session() as session:
        car_service = get_car_service(
            get_car_repository(session)
        )
        repair_service = get_repair_service(
            get_repair_repository(session)
        )

        desc = message.text.strip()
        data = await state.get_data()
        car_name = data['car_name']
        user_id = message.from_user.id
        car_id = await car_service.get_car_or_id(
            car_name=car_name,
            user_id=user_id
        )

        await repair_service.create_repair_note(
            repair_desc=desc,
            mileage=data['mileage'],
            car_id=car_id
        )

        await state.clear()
        cached_data.pop(user_id, None)

    await message.reply('Запись добавлена!')


@state_router.message(CarDelete.confirmation)
async def delete_car(message: Message, state: FSMContext):
    await message.answer(
        'Можно отменить свой выбор',
        reply_markup=car_delete_kb
    )


@state_router.message(CarRename.name)
async def rename_car(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text.strip()
    if new_name.startswith('/'):
        await message.reply(
            'Название не может начинаться с <b>/</b>',
            parse_mode='Html'
        )
    else:
        async with get_async_session() as session:
            car_service = get_car_service(
                get_car_repository(session)
            )
            data = await state.get_data()
            car_name = data['car_name']
            car: Car = await car_service.get_car_or_id(
                car_name,
                user_id,
                instance_mode=True
            )
            await car_service.rename_car(car, car_name)

            await message.answer(
                f'Название <b>{new_name}</b> сохранено.',
                parse_mode='Html'
            )
            cached_data.pop(user_id, None)
            await state.clear()
