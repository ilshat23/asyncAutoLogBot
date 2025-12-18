from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from core.cache import cached_data
from core.dependencies import (
    get_async_session, get_user_repository, get_user_service,
    get_car_repository, get_car_service
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils.keyboards import inline_cars, main_menu_keyboard
from routers.user_states import CarReg


handler_router = Router()


@handler_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    user_exists = True

    user_repo = get_user_repository(session)
    user_service = get_user_service(user_repo)

    user = await user_service.get_user(user_id)

    if not user:
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        await user_service.create_user(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user_exists = False

    msg_text = f'Вы {"уже" if user_exists else ""} зарегистрированы.'
    await message.answer(msg_text)

    if not user_exists:
        await state.set_state(CarReg.name)
        await message.answer(
            'По какому автомобилю хочешь завести сервисную книгу📕? '
            'В дальнейшем можно будет добавить еще автомобили. Для '
            'навигации используй команду <b>/menu</b>',
            parse_mode='Html'
        )


@handler_router.message(Command('menu'))
async def main_handler(message: Message):
    await message.answer(
        'Выбери нужную опцию из меню.',
        reply_markup=main_menu_keyboard
    )


@handler_router.message(F.text == '✅ Добавить новый автомобиль')
async def add_car_handler(message: Message, state: FSMContext):
    name = message.from_user.first_name
    await message.answer(f'{name}, введи название нового автомобиля.')
    await state.set_state(CarReg.name)
    cached_data['user_id'] = message.from_user.id
    cached_data['first_name'] = name


@handler_router.message(F.text == '🚘 Показать все автомобили')
async def show_cars_handler(message: Message, session: AsyncSession):
    car_service = get_car_service(
        get_car_repository(session)
    )
    user_id = message.from_user.id
    cars = await car_service.get_cars(user_id)

    if not cars:
        await message.answer('У тебя нет автомобилей в коллекции.')
    else:
        await message.answer(
            'Твои автомобили.',
            reply_markup=await inline_cars(cars, user_id)
        )


@handler_router.message(
    lambda m: m.text.lower() in {
        'menu', 'men',
        'меню', 'мен'
    }
)
async def menu_words_handler(message: Message):
    await message.answer(
        'Выбери нужную опцию из меню.',
        reply_markup=main_menu_keyboard
    )


@handler_router.message(StateFilter(None))
async def any_words_handler(message: Message):
    if message.text not in {
        '↩️ Назад',
        '✅ Добавить новый автомобиль',
        '🚘 Показать все автомобили'
    }:
        await message.reply(
            '❗️Я не понял сообщение.❗️\nИспользуй команду <b>/menu</b>. '
            'Там есть все необходимое для тебя.',
            parse_mode='HTML'
        )
