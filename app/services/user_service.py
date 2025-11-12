from core.cache import cached_data
from core.database.models import User
from repositories.user_repository import UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user(self, telegram_id: int) -> User:
        if telegram_id in cached_data:
            return cached_data[telegram_id]

        user = await self.user_repository.get_user(telegram_id=telegram_id)
        cached_data[telegram_id] = user
        return user

    async def create_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str | None = None,
        last_name: str | None = None
    ) -> User:
        user = await self.user_repository.create_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        return user

    async def get_or_create(
        self,
        telegram_id: int,
        username: str,
        first_name: str | None = None,
        last_name: str | None = None
    ) -> tuple[bool, User]:
        user = await self.get_user(telegram_id=telegram_id)

        if not user:
            user = await self.create_user(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            return True, user

        return False, user
