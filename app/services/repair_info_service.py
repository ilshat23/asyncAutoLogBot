from typing import Sequence

from core.database.models import RepairHistory
from repositories.repair_info_repository import RepairHistoryRepository


class RepairHistoryService:
    def __init__(self, repair_history_repo: RepairHistoryRepository):
        self.repair_history_repo = repair_history_repo

    async def create_repair_note(
        self, repair_desc: str, mileage: int, car_id: int
    ):
        _ = await self.repair_history_repo.create_note(
            repair_description=repair_desc,
            mileage=mileage,
            car_id=car_id
        )

    async def get_repair_history(self, car_id: int) -> Sequence[RepairHistory]:
        notes = await self.repair_history_repo.get_repair_history(car_id)
        return notes

    async def clear_car_history(self, car_id: int):
        await self.repair_history_repo.clear_repair_history(car_id)
