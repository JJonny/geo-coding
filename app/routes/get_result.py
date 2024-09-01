import json

from flask import Blueprint, Response

from app.database import async_session, sync_session
from app.models import Task, Location

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


get_result_bp = Blueprint('get_result', __name__)


@get_result_bp.route('/getResult/<uuid:result_id>', methods=['GET'])
def get_result_route(result_id):
    with sync_session() as session:
        task: Task = session.query(Task).filter_by(id=result_id).one_or_none()

        if task is None:
            raise ValueError(f"Task with ID {result_id} not found.")

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

        result = json.dumps(result, ensure_ascii=False, indent=4)

        return Response(result, mimetype='application/json')
