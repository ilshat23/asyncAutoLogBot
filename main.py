import asyncio
import logging
import os
from datetime import datetime as dt

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.callbacks import callback_router
from app.handlers import handler_router
from app.user_states import state_router
from app.utils import send_err_msg
from telegram_client import TelegramClient


load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN = os.getenv('ADMIN_CHAT_ID')

if TOKEN is None:
    raise ValueError('Token must be str')

bot = Bot(TOKEN)
dp = Dispatcher()
tg = TelegramClient(TOKEN, 'https://api.telegram.org')
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(FORMATTER)
logger.addHandler(console_handler)


def create_error_message(err: Exception) -> str:
    return (f'{dt.now().strftime("%Y/%m/%d %H:%M")} --- '
            f'{err.__class__} --- {err}')


async def main():
    try:
        dp.include_router(callback_router)
        dp.include_router(handler_router)
        dp.include_router(state_router)
        await dp.start_polling(bot)
    except Exception as error:
        await send_err_msg(tg, error, ADMIN)


if __name__ == '__main__':
    asyncio.run(main())
