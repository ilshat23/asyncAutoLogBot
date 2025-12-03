import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from core.middlewares import SessionMiddleware
from clients.telegram_client import TelegramClient
from routers.car_action_callbacks import car_action_router
from routers.car_confirmation_callbacks import car_confirmation_router
from routers.menu_handlers import handler_router
from routers.user_states import state_router
from utils.utils import send_err_msg


def setup_app() -> tuple[Bot, Dispatcher, TelegramClient, str]:
    """Инициализация приложения."""
    load_dotenv()

    TOKEN = os.getenv('TOKEN')
    ADMIN = os.getenv('ADMIN_CHAT_ID')

    if TOKEN is None:
        raise ValueError('Token must be str')

    if ADMIN is None:
        raise ValueError('ADMIN_ID must be str')

    bot = Bot(TOKEN)
    dp = Dispatcher()
    tg = TelegramClient(TOKEN)

    return bot, dp, tg, ADMIN


def setup_logging():
    """Настройка логгирования."""
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)


def include_routers(dp: Dispatcher):
    """Добавление всех роутеров."""
    dp.include_router(car_action_router)
    dp.include_router(car_confirmation_router)
    dp.include_router(handler_router)
    dp.include_router(state_router)


async def main():
    """Сборка всех частей и запуск приложения."""
    bot, dp, tg_client, admin_chat_id = setup_app()
    dp.update.middleware(SessionMiddleware())
    setup_logging()
    include_routers(dp)

    try:
        await dp.start_polling(bot)
    except Exception as error:
        await send_err_msg(tg_client, error, admin_chat_id)


if __name__ == '__main__':
    asyncio.run(main())
