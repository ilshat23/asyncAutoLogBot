from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine('sqlite+aiosqlite:///autolog.db', echo=True)
async_session = async_sessionmaker(engine,
                                   expire_on_commit=False,
                                   class_=AsyncSession)


class Base(DeclarativeBase):
    pass
