from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.async_database_url)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession
)

class Base(DeclarativeBase):
    pass
