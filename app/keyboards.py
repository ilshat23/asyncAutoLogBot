from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.cache import cached_data


car_delete_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, удалить 😢', callback_data='delete')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])


async def inline_cars(cars: list,
                      user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for car in cars:
        car_name = car.car_name
        keyboard.add(
            InlineKeyboardButton(text=car_name,
                                 callback_data=f'select:{car_name}')
        )
        if user_id not in cached_data:
            cached_data[user_id] = {car_name: car.id}
        else:
            cached_data[user_id].update({car_name: car.id})
    keyboard.add(
        InlineKeyboardButton(text='Назад ↩️', callback_data='back')
    )

    return keyboard.adjust(2).as_markup()


main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✅ Добавить новый автомобиль'),
     KeyboardButton(text='🚘 Показать все автомобили')],
    [KeyboardButton(text='↩️ Назад')]
], resize_keyboard=True,
   input_field_placeholder='⬇️ Воспользуйся меню ниже. ⬇️',
   one_time_keyboard=True)

what_to_do_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Добавить запись о ремонте',
                          callback_data='add_service_notation'),
     InlineKeyboardButton(text='✏️ Поменять название автомобиля',
                          callback_data='rename')],
    [InlineKeyboardButton(text='❌ Удалить автомобиль',
                          callback_data='delete_my_car'),
     InlineKeyboardButton(text='📖 Сервисная история',
                          callback_data='show_history')],
    [InlineKeyboardButton(text='❌ Очистить историю',
                          callback_data='clear_history'),
     InlineKeyboardButton(text='↩️ Назад',
                          callback_data='back')]
])
