from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.cache import cached_data
from core.dependencies import (
    get_async_session, get_car_repository, get_car_service,
    get_repair_repository, get_repair_service
)
from utils.keyboards import car_delete_kb, history_delete_kb, what_to_do_kb
from routers.user_states import RepairInfoReg, CarRename


car_action_router = Router()


@car_action_router.callback_query(F.data.startswith('select'))
async def choice_handler(callback: CallbackQuery):
    car_name = callback.data.split(':')[-1]

    await callback.message.edit_text(
        f'Что хочешь сделать с {car_name}?',
        reply_markup=what_to_do_kb(car_name)
    )


@car_action_router.callback_query(F.data.startswith('add_service_notation'))
async def add_sn_callback(callback: CallbackQuery,
                          state: FSMContext) -> None:
    car_name = callback.data.split(':')[-1]
    await callback.answer(f'Ты выбрал {car_name}!')
    await callback.message.edit_text(
        f'А теперь введи пробег от {car_name}.',
        reply_markup=None
    )
    await state.set_state(RepairInfoReg.mileage)
    await state.update_data(car_name=car_name)


@car_action_router.callback_query(F.data.startswith('delete_my_car'))
async def del_my_car_callback(callback: CallbackQuery):
    car_name = callback.data.split(':')[-1]
    user_id = callback.from_user.id

    if user_id not in cached_data:
        await callback.message.answer(
            'Ошибка удаления автомобиля, попробуй снова'
        )
        return

    cached_data[callback.from_user.id].update({'selected_car': car_name})

    await callback.answer(f'Ты выбрал {car_name}!')
    await callback.message.edit_text(
        'Уверен, что хочешь удалить?',
        reply_markup=car_delete_kb
    )


@car_action_router.callback_query(F.data.startswith('show_history'))
async def show_history(callback: CallbackQuery):
    async with get_async_session() as session:
        car_service = get_car_service(
            get_car_repository(session)
        )
        repair_service = get_repair_service(
            get_repair_repository(session)
        )
        user_id = callback.from_user.id
        car_name = callback.data.split(':')[-1]
        car_id: int = await car_service.get_car_or_id(car_name, user_id)
        await callback.answer(f'Ты выбрал {car_name}!')

        notes = await repair_service.get_repair_history(car_id)

        if notes:
            result_message = [f'📒История по {car_name}:']

            for note in notes:
                created_at = note.repair_date
                mileage = note.mileage
                desc = note.repair_description

                text = (
                    f'1️⃣Запись от 📅 {created_at}.\n'
                    f'2️⃣Пробег: 🚚 <b>{mileage}</b> км.\n'
                    f'3️⃣Выполненные действия🔧:\n<i>{desc}</i>.'
                )
                result_message.append(text)
            await callback.message.edit_text('\n\n\n'.join(result_message),
                                             parse_mode='Html')
        else:
            await callback.message.edit_text('История пуста.')

        cached_data.pop(user_id, None)


@car_action_router.callback_query(F.data.startswith('clear_history'))
async def clear_car_history_callback(callback: CallbackQuery):
    car_name = callback.data.split(':')[-1]
    user_id = callback.from_user.id

    if user_id not in cached_data:
        await callback.answer('Возникла ошибка обработки, попробуй снова.')
    cached_data[user_id].update({'selected_car': car_name})

    await callback.message.answer(
        'История очистится безвозвратно!',
        reply_markup=history_delete_kb
    )


@car_action_router.callback_query(F.data.startswith('rename'))
async def rename_car(callback: CallbackQuery, state: FSMContext):
    car_name = callback.data.split(':')[-1]
    await state.set_state(CarRename.name)
    await state.update_data(car_name=car_name)
    await callback.message.edit_text('Введи новое название.')
