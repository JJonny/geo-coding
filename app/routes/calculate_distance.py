import io
import logging
import uuid

from flask import Blueprint, request, jsonify, current_app

from app.database import sync_session
from app.data_access.models.models import Distance, Point, PointAddress
from app.data_access.task_manager import save_results_by_task_id
from app.models import TaskStatus
from app.services.tasks import reverse_geocode_and_calculate_distances
from app.utils.file_processing import process_file_data

from app.data_access.repositories.repository_factory import RepositoryFactory


logger = logging.getLogger(__name__)
calculate_distance_bp = Blueprint('calculate_distance', __name__)


@calculate_distance_bp.route('/calculateDistance', methods=['POST'])
def calculate_distance_route():
    """Calculate distance endpoint."""

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        with sync_session() as session:
            repository_factory = RepositoryFactory(app=current_app)

            repository = repository_factory.get_repository(session)
            task_data = {"status": TaskStatus.RUNNING}
            task_id = repository.create_task(task_data)

        file_data = io.StringIO(file.read().decode('utf-8'))
        points: list[Point] = process_file_data(file_data)

        # local_calc(points, task_id)
        reverse_geocode_and_calculate_distances.apply_async(args=[points, task_id])

        task_status_obj = task_data.get("status", None)
        task_status = task_status_obj.RUNNING.value if task_status_obj else ''

        return jsonify({"task_id": task_id, "status": task_status}), 200


def local_calc(points: list[Point], task_id: uuid.UUID):
    """Util func for testing localy without celery"""
    from app.utils.file_processing import process_geo_data

    task_data: dict[str, [Distance | PointAddress]] = process_geo_data(points)
    save_results_by_task_id(task_id=task_id, task_data=task_data)

