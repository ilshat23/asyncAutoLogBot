from datetime import datetime as dt

from clients.telegram_client import TelegramClient


async def send_err_msg(
    tg: TelegramClient,
    err: Exception,
    admin: str | None = None
):

    msg = (
        f'{dt.now().strftime("%Y/%m/%d %H:%M")} --- {err.__class__} --- {err}'
    )

    await tg.post(
        'sendMessage',
        params={
            'text': msg,
            'chat_id': admin
        }
    )
