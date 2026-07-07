from fastapi import FastAPI
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import app.api.models
from app.api.models.base import Base
from app.api.models.user_role import UserRoleBase
from .config import settings

context: AsyncEngine = create_async_engine(settings.DB_URL, echo=True)
AsyncSessionLocal: async_sessionmaker = async_sessionmaker(context, expire_on_commit=False, autoflush=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with context.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        stmt = select(UserRoleBase)
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            session.add_all([
                UserRoleBase.S_ADMIN(),
                UserRoleBase.ADMIN(),
                UserRoleBase.USER(),
            ])
            await session.commit()
    yield
    
async def get_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session