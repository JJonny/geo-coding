import logging
import uuid

from flask import current_app
from app.database import sync_session
from app.data_access.models.models import Distance, PointAddress
from app.data_access.repositories.repository_factory import RepositoryFactory
from app.models import Location, Task, TaskStatus

logger = logging.getLogger(__name__)


def _get_repository(session):
    return RepositoryFactory(app=current_app).get_repository(session)


def get_all_by_task_id(task_id: uuid.UUID) -> dict:
    """Get all info by task id."""
    with sync_session() as session:
        repository = _get_repository(session)
        task: Task = repository.get_task(task_id=task_id)

        if task is None:
            logger.error("Task with ID %s not found.", task_id)
            raise ValueError(f"Task with ID {task_id} not found.")

        locations: list[Location] = task.locations
        addresses = [
            {"name": addr.name, "address": addr.address}
            for addr in locations
        ]

        return {
            "task_id": str(task.id),
            "status": task.status.value,
            "data": {
                "points": addresses,
                "links": task.distances,
            },
        }


def save_results_by_task_id(task_id: uuid.UUID, task_data: dict[str, list[Distance | PointAddress]]) -> None:
    """Save results to DB."""
    with sync_session() as session:
        repository = _get_repository(session)
        repository.update_task(task_id=task_id, task_data=task_data)


def set_task_failed(task_id: uuid.UUID) -> None:
    """Mark task as FAILED in DB."""
    with sync_session() as session:
        repository = _get_repository(session)
        task = repository.get_task(task_id=task_id)
        if task:
            task.status = TaskStatus.FAILED
            session.commit()
