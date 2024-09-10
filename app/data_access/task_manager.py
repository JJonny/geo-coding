import logging
import uuid

from flask import current_app

from app.config import settings
from app.database import sync_session
from app.data_access.repositories.repository_factory import RepositoryFactory
from app.models import Task, Location


def get_all_by_task_id(task_id: uuid.UUID) -> dict:
    """Get all info by task id."""

    repository_factory = RepositoryFactory(app=current_app)
    result = {}

    if settings.MONGO:
        with sync_session() as session:
            repository = repository_factory.get_repository(session)
            task: Task = repository.get_task(task_id=task_id)

            if task is None:
                logging.error(f"Task with ID {task_id} not found.")
                raise ValueError(f"Task with ID {task_id} not found.")

            locations: list[Location] = task.locations
            addresses = [
                {
                    "name": addr.name,
                    "address": addr.address,
                }
                for addr in locations
            ]

            result = {
                "task_id": str(task.id),
                "status": task.status,
                "data": {
                    "points": addresses,
                    "links": task.distances
                },
            }
    else:
        repository = repository_factory.get_repository()
        task: dict = repository.get_task(task_id=task_id)

        result = {
            "task_id": task["_id"],
            "status": task.get("status", "unknown"),
            "data": {
                "points": task.get("points", []),
                "links": task.get("distances", [])
            },
        }

    return result


def save_results_by_task_id(task_id: uuid.UUID, task_data: dict):
    """Save results to DB."""

    # with sync_session() as session:
    repository_factory = RepositoryFactory(app=current_app)
    repository = repository_factory.get_repository()
    repository.update_task(task_id=task_id, task_data=task_data)

