import logging

from app.data_access.interfaces.database_interface import DatabaseInterface
from app.data_access.repositories.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """Factory to manage repositories."""

    def __init__(self, app):
        self.app = app

    def get_repository(self, db_session=None) -> DatabaseInterface:
        """Return repository depends on configuration."""
        if self.app.config.get("MONGO", None) is None:
            if db_session is None:
                logger.error(f"Session shouldn't be None for Postgres repository.")
                raise Exception("Session shouldn't be None")
            return PostgresRepository(db_session)
