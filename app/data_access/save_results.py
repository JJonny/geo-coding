import uuid

from sqlalchemy import insert

from app.database import sync_session
from app.models import Task, Location


def save_results_to_db(data: dict, task_id: uuid.UUID):
    """Save results to DB."""

    try:
        with sync_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                raise ValueError(f"Task with ID {task_id} not found.")

            distances_json = [
                {
                    'name': link['name'],
                    'distance': link['distance']
                }
                for link in data['links']
            ]

            task.distances = distances_json
            task.status = 'done'

            session.add(task)

            points_entries = [
                {
                    'id': uuid.uuid4(),
                    'task_id': task_id,
                    'name': point['name'],
                    'address': point['address'],
                    'latitude': point['lat'],
                    'longitude': point['lon']
                }
                for point in data['points']
            ]

            if points_entries:
                session.execute(insert(Location).values(points_entries))

            session.flush()
            session.commit()


    except Exception as e:
        session.rollback()
        raise e
