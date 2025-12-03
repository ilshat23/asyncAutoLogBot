from typing import Callable, Any

from aiogram import BaseMiddleware
from aiogram.types import Update

from .dependencies import get_async_session


class SessionMiddleware(BaseMiddleware):
    """Миддлвари для инъекции сессии в хэндлеры."""

    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: dict[str, Any]
    ) -> Any:
        async with get_async_session() as session:
            data['session'] = session
            return await handler(event, data)
