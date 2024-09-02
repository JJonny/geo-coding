import uuid

from app.database import sync_session
from app.models import Task, Location


def get_all_by_task_id(task_id: uuid.UUID) -> dict:
    """Get all info by task id."""

    with sync_session() as session:
        task: Task = session.query(Task).filter_by(id=task_id).one_or_none()

        if task is None:
            raise ValueError(f"Task with ID {task_id} not found.")

        locations: Location = task.locations
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

        return result
