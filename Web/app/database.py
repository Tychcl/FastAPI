from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from .config import settings

context: AsyncEngine = create_async_engine(settings.DB_URL, echo=True)
AsyncSessionLocal: async_sessionmaker = async_sessionmaker(context, expire_on_commit=False, autoflush=False)
    
async def get_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session