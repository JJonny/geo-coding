from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase


from app.config import settings


sync_engine = create_engine(settings.sync_db_connection, echo=True, pool_pre_ping=True)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async_engine = create_async_engine(settings.async_db_connection, echo=True)
async_session = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
