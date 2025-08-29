from typing import Optional

from aiohttp import ClientSession


class TelegramClient:
    def __init__(self, api_token: str, base_url: str) -> None:
        self.api_token = api_token
        self.base_url = base_url

    async def _prepare_url(self, method: str) -> str:
        full_url = f'{self.base_url}/bot{self.api_token}/'

        if method:
            full_url += method

        return full_url

    async def post(self, method: str,
                   params: Optional[dict] = None,
                   body: Optional[dict] = None) -> dict | list:
        url = await self._prepare_url(method)

        async with ClientSession() as session:
            async with session.post(url, params=params, json=body) as response:
                json_response = await response.json()
                return json_response
