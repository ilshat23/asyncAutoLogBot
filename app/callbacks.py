from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import delete
from sqlalchemy.future import select

from app.cache import cached_data
from app.database.db import async_session
from app.database.models import RepairHistory
from app.keyboards import car_delete_kb, what_to_do_kb
from app.utils import delete_car, get_car_and_update_cache
from app.user_states import RepairInfoReg, RenameState


callback_router = Router()


@callback_router.callback_query(F.data.startswith('add_service_notation'))
async def add_sn_callback(callback: CallbackQuery,
                          state: FSMContext) -> None:
    car_name = await get_car_and_update_cache(callback)
    await callback.answer(f'Ты выбрал {car_name}!')
    await callback.message.edit_text(f'А теперь введи пробег от {car_name}.',
                                     reply_markup=None)
    await state.set_state(RepairInfoReg.mileage)


@callback_router.callback_query(F.data.startswith('delete_my_car'))
async def del_my_car_callback(callback: CallbackQuery) -> None:
    car_name = await get_car_and_update_cache(callback)
    await callback.answer(f'Ты выбрал {car_name}!')
    await callback.message.edit_text('Уверен, что это нужно?',
                                     reply_markup=car_delete_kb)


@callback_router.callback_query(F.data == 'delete')
async def delete_car_totally(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    car_id = cached_data[callback.from_user.id].get('selected_car_id')
    if car_id is None:
        raise TypeError('car_id не может быть None')
    await delete_car(car_id)
    await callback.message.edit_text(f'{cached_data[user_id].get('selected_car')} со '
                                     'всеми записями удалён.')
    cached_data.clear()
    await state.clear()


@callback_router.callback_query(F.data == 'cancel')
async def cancel_deleting(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.message.edit_text(f'Удаление {cached_data[user_id].get('car_name')} '
                                     'отменено.')
    cached_data.clear()
    await state.clear()


@callback_router.callback_query(F.data.startswith('select'))
async def choice_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    car_name = callback.data.split(':')[-1]

    cached_data[user_id]['selected_car'] = car_name
    await callback.message.edit_text(f'Что хочешь сделать с {car_name}?',
                                     reply_markup=what_to_do_kb)


@callback_router.callback_query(F.data == 'back')
async def get_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    cached_data.clear()
    await state.clear()


@callback_router.callback_query(F.data == 'show_history')
async def show_history(callback: CallbackQuery):
    car_name = await get_car_and_update_cache(callback)
    car_id = cached_data[callback.from_user.id].get(car_name)
    await callback.answer(f'Ты выбрал {car_name}!')
    async with async_session() as session:
        res = await session.execute(
            select(RepairHistory).where(RepairHistory.car_id == car_id)
        )
        notes = res.scalars().all()

        if notes:
            result_message = [f'📒История по {car_name}:']

            for note in notes:
                created_at = note.repair_date
                mileage = note.mileage
                desc = note.repair_description

                text = (f'1️⃣Запись от 📅 {created_at}.\n'
                        f'2️⃣Пробег: 🚚 <b>{mileage}</b> км.\n'
                        f'3️⃣Выполненные действия🔧:\n<i>{desc}</i>.')
                result_message.append(text)
            await callback.message.edit_text('\n\n\n'.join(result_message),
                                             parse_mode='Html')
        else:
            await callback.message.edit_text('История пуста.')


@callback_router.callback_query(F.data == 'clear_history')
async def clear_car_history(callback: CallbackQuery):

    car_name = await get_car_and_update_cache(callback)
    car_id = cached_data[callback.from_user.id].get(car_name)
    cached_data.clear()

    async with async_session() as session:
        await session.execute(
            delete(RepairHistory).where(RepairHistory.car_id == car_id)
        )
        await session.commit()

    await callback.message.edit_text(f'История <b>{car_name}</b> удалена.',
                                     parse_mode='Html')


@callback_router.callback_query(F.data == 'rename')
async def rename_car(callback: CallbackQuery, state: FSMContext):
    _ = await get_car_and_update_cache(callback)
    await state.set_state(RenameState.name)
    await callback.message.edit_text('Введи новое название.')
