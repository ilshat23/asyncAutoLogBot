import logging as lg
from typing import Optional


from aiohttp import (
    ClientError, ClientResponseError, ClientSession, ClientTimeout
)


logger = lg.getLogger(__name__)


class TelegramClient:
    BASE_URL = 'https://api.telegram.org'

    def __init__(self, api_token: str, timeout: float = 30.0) -> None:
        self.api_token = api_token
        self.timeout = ClientTimeout(total=timeout)

    def _prepare_url(self, method: str) -> str:
        """Подготавливает URL для запроса."""
        method = method.lstrip('/')
        return f'{self.BASE_URL}/bot{self.api_token}/{method}'

    async def post(
        self,
        method: str,
        params: Optional[dict] = None,
        body: Optional[dict] = None
    ) -> dict | list | None:
        """Делает POST-запрос к Telegram API."""
        url = self._prepare_url(method)

        async with ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    url,
                    params=params,
                    json=body,
                    raise_for_status=True
                ) as response:
                    json_response = await response.json()
                    return json_response
            except ClientResponseError as e:
                logger.error(
                    f'Telegram API error {method}: {e.status} - {e.message}'
                )
            except ClientError as e:
                logger.error(
                    f'Network error in {method}: {str(e)}'
                )
            except Exception as e:
                logger.error(
                    f'Unexpected error in {method}: {str(e)}'
                )

        return None
