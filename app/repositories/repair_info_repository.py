from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import RepairHistory


class RepairHistoryRepository:
    """Репозиторий для работы с сервисной историей автомобиля."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_note(
        self,
        repair_description: str,
        mileage: int,
        car_id: int
    ) -> RepairHistory:
        note = RepairHistory(
            repair_description=repair_description,
            mileage=mileage,
            car_id=car_id
        )
        self.session.add(note)
        return note

    async def get_repair_history(self, car_id: int) -> Sequence[RepairHistory]:
        """
        Возвращает всю сервисную историю автомобиля.

        Args:
            car_id (int): Идентификатор автомобиля.

        Returns:
            Sequence[RepairHistory]: Последовательность из сервисных записей.
        """
        stmt = select(RepairHistory).filter(RepairHistory.car_id == car_id)
        res = await self.session.scalars(stmt)
        return res.all()

    async def clear_repair_history(self, car_id: int):
        stmt = delete(RepairHistory).filter(RepairHistory.car_id == car_id)
        await self.session.execute(stmt)
