import uuid
from uuid import uuid4

from geoalchemy2.elements import WKTElement
from sqlalchemy import insert, text

from app.models import Task, Location, TaskStatus
from app.data_access.interfaces.database_interface import DatabaseInterface
from app.data_access.models.models import PointAddress


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

    def update_task(self, task_id, task_data: dict[str, list[PointAddress]]):
        """Update task by task_id. Saves locations with PostGIS geometry and
        computes pairwise distances via ST_Distance."""
        task: Task = self.get_task(task_id=task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found.")

        task.status = TaskStatus.DONE
        self.db_session.add(task)

        points_entries = [
            {
                "id": uuid.uuid4(),
                "task_id": task_id,
                "name": point.name,
                "address": point.address,
                "latitude": point.lat,
                "longitude": point.lon,
                "geo_point": WKTElement(
                    f"POINT({point.lon} {point.lat})", srid=4326
                ),
            }
            for point in task_data["points"]
        ]

        if points_entries:
            self.db_session.execute(insert(Location).values(points_entries))
            self.db_session.flush()

            result = self.db_session.execute(
                text(
                    """
                    SELECT
                        l1.name || l2.name AS name,
                        ST_Distance(l1.geo_point, l2.geo_point) AS distance
                    FROM geo_app.locations l1
                    JOIN geo_app.locations l2
                        ON l1.task_id = l2.task_id AND l1.id < l2.id
                    WHERE l1.task_id = :task_id
                    """
                ),
                {"task_id": str(task_id)},
            )
            task.distances = [
                {"name": row.name, "distance": row.distance} for row in result
            ]

        self.db_session.commit()
