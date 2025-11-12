from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.cache import cached_data
from core.database.models import Car


car_delete_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да, удалить 😢', callback_data='delete')],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
    ]
)

history_delete_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Очистить историю', callback_data='clear')],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
    ]
)

async def inline_cars(
    cars: list[Car],
    user_id: int
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if user_id not in cached_data:
        cached_data[user_id] = {'cars': {}}

    for car in cars:
        car_name = car.car_name
        keyboard.add(
            InlineKeyboardButton(
                text=car_name,
                callback_data=f'select:{car_name}'
            )
        )
        cached_data[user_id]['cars'].update({car_name: car.id})
    keyboard.add(
        InlineKeyboardButton(text='Назад ↩️', callback_data='back')
    )

    return keyboard.adjust(2).as_markup()


main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='✅ Добавить новый автомобиль'),
        KeyboardButton(text='🚘 Показать все автомобили')
    ],
    [KeyboardButton(text='↩️ Назад')]
], resize_keyboard=True,
    input_field_placeholder='⬇️ Воспользуйся меню ниже. ⬇️',
    one_time_keyboard=True)


def what_to_do_kb(car_name: str) -> InlineKeyboardMarkup:
    what_to_do_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Добавить запись о ремонте',
                    callback_data=f'add_service_notation:{car_name}'
                ),
                InlineKeyboardButton(
                    text='✏️ Поменять название автомобиля',
                    callback_data=f'rename:{car_name}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Удалить автомобиль',
                    callback_data=f'delete_my_car:{car_name}'
                ),
                InlineKeyboardButton(
                    text='📖 Сервисная история',
                    callback_data=f'show_history:{car_name}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Очистить историю',
                    callback_data=f'clear_history:{car_name}'
                ),
                InlineKeyboardButton(
                    text='↩️ Назад',
                    callback_data='back'
                )
            ]
        ]
    )
    return what_to_do_kb
