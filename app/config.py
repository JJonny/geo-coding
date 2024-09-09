import logging
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
BASE_DIR = Path(__file__).parents[1]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Config:
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    DB_DATA_FOLDER = BASE_DIR / 'data/db'

    REDIS_URL = os.getenv('REDIS_URL')
    DEBUG = int(os.getenv('DEBUG', 0))

    if DEBUG:
        CELERY_BROKER_URL = 'redis://localhost:6379/1'
        CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    else:
        CELERY_BROKER_URL = REDIS_URL
        CELERY_RESULT_BACKEND = REDIS_URL

    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    if DEBUG:
        POSTGRES_HOST = 'localhost'
    else:
        POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB')

    @property
    def sync_db_connection(self):
        return (f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")


settings = Config()
