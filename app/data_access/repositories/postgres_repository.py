import uuid
from uuid import uuid4

from sqlalchemy import insert

from app.models import Task, Location, TaskStatus
from app.data_access.interfaces.database_interface import DatabaseInterface
from app.data_access.models.models import Distance, PointAddress


class PostgresRepository(DatabaseInterface):
    """Postgres Implementation"""
    def __init__(self, session):
        self.db_session = session

    def create_task(self, task_data: dict) -> uuid.UUID:
        """Create new task."""
        task_id = uuid4()
        new_task = Task(id=task_id, **task_data)
        self.db_session.add(new_task)
        self.db_session.commit()
        return task_id

    def get_task(self, task_id: uuid.UUID) -> Task:
        """Get task by task_id."""
        task: Task = self.db_session.query(Task).filter_by(id=task_id).one_or_none()
        return task

    def update_task(self, task_id, task_data: dict[str, [Distance | PointAddress]]):
        """Update task by taks_id"""
        task: Task = self.get_task(task_id=task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found.")

        task.distances = [item._asdict() for item in task_data['links']]
        task.status = TaskStatus.DONE

        self.db_session.add(task)

        points_entries = [
            {
                'id': uuid.uuid4(),
                'task_id': task_id,
                'name': point.name,
                'address': point.address,
                'latitude': point.lat,
                'longitude': point.lon,
            }
            for point in task_data['points']
        ]

        if points_entries:
            self.db_session.execute(insert(Location).values(points_entries))

        self.db_session.flush()
        self.db_session.commit()
