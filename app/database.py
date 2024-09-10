from flask import current_app

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

sync_engine = create_engine(settings.sync_db_connection, echo=False, pool_pre_ping=True)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_mongo_db():
    return current_app.mongo_client['mydatabase']

def close_mongo_connection(e=None):
    # mongo_client = g.pop('mongo_client', None)

    if current_app.mongo_client is not None:
        current_app.mongo_client.close()

class Base(DeclarativeBase):
    pass
