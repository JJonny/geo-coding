# app/data_access/interfaces/database_interface.py
import uuid
from abc import ABC, abstractmethod


from app.models import Task


class DatabaseInterface(ABC):
    @abstractmethod
    def create_task(self, task_data: dict) -> uuid.UUID:
        pass

    @abstractmethod
    def get_task(self, task_id: uuid.UUID) -> Task:
        pass

    @abstractmethod
    def update_task(self, task_id: uuid.UUID, task_data: dict):
        pass