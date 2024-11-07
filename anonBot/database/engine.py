from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

from config import DB_LITE

engine = create_async_engine(url=DB_LITE, echo = False)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)
        
        

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


        


