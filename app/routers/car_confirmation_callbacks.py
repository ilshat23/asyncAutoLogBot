from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.cache import cached_data
from core.dependencies import (
    get_async_session, get_car_repository, get_car_service,
    get_repair_repository, get_repair_service
)
from core.database.models import Car


car_confirmation_router = Router()


@car_confirmation_router.callback_query(F.data == 'delete')
async def delete_car_totally(callback: CallbackQuery):
    user_id = callback.from_user.id
    car_name = cached_data[callback.from_user.id].get('selected_car')

    if car_name is None:
        await callback.message.answer(
            'При удалении возникла ошибка, попробуй снова.'
        )
        return

    async with get_async_session() as session:
        car_service = get_car_service(
            get_car_repository(session)
        )

        car: Car = await car_service.get_car_or_id(
            car_name,
            user_id,
            instance_mode=True
        )
        await car_service.delete_car(car)

    await callback.message.edit_text(
        f'{car_name} со всеми записями удалён.'
    )
    cached_data.pop(user_id, None)


@car_confirmation_router.callback_query(F.data == 'clear')
async def clear_car_history(callback: CallbackQuery):
    async with get_async_session() as session:
        car_service = get_car_service(
            get_car_repository(session)
        )
        repair_service = get_repair_service(
            get_repair_repository(session)
        )
        user_id = callback.from_user.id
        car_name = cached_data[user_id].get('selected_car')

        if car_name is None:
            callback.message.reply('Произошла ошибка, попробуй снова.')

        car_id: int = await car_service.get_car_or_id(car_name, user_id)
        await repair_service.clear_car_history(car_id)
        cached_data.pop(callback.from_user.id, None)

        await callback.message.edit_text(
            f'История <b>{car_name}</b> удалена.',
            parse_mode='Html'
        )


@car_confirmation_router.callback_query(F.data == 'cancel')
async def cancel_deleting(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        'Удаление отменено.'
    )
    cached_data.pop(user_id, None)
    await state.clear()


@car_confirmation_router.callback_query(F.data == 'back')
async def get_back(callback: CallbackQuery, state: FSMContext):
    """Удаляет текущее сообщение и очищает кэш вместе с состоянием."""
    await callback.message.delete()
    cached_data.pop(callback.from_user.id, None)
    await state.clear()
