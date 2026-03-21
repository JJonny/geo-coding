from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

sync_engine = create_engine(settings.sync_db_connection, echo=False, pool_pre_ping=True)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


class Base(DeclarativeBase):
    pass
