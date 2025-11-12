from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User


class UserRepository:
    """Репозиторий для работы с моделью пользователя."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str | None = None,
        last_name: str | None = None
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.refresh(user)
        return user

    async def get_user(self, telegram_id: int) -> User:
        user = await self.session.get(User, telegram_id)
        return user
