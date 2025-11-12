from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database.db import AsyncSessionLocal
from .exceptions import CarExistsError
from repositories.car_repository import CarRepository
from repositories.repair_info_repository import RepairHistoryRepository
from repositories.user_repository import UserRepository
from services.car_service import CarService
from services.repair_info_service import RepairHistoryService
from services.user_service import UserService


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except IntegrityError as err:
        if 'uq_user_car_name' in str(err):
            raise CarExistsError(
                'Автомобиль с таким названием уже существует:'
            )
        raise
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


def get_user_service(user_repo: UserRepository) -> UserService:
    return UserService(user_repo)


def get_car_repository(session: AsyncSession) -> CarRepository:
    return CarRepository(session)


def get_car_service(car_repo: CarRepository) -> CarService:
    return CarService(car_repo)


def get_repair_repository(session: AsyncSession) -> RepairHistoryRepository:
    return RepairHistoryRepository(session)


def get_repair_service(
    repair_repo: RepairHistoryRepository
) -> RepairHistoryService:
    return RepairHistoryService(repair_repo)
