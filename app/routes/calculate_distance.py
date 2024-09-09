import io
from uuid import uuid4

from flask import Blueprint, request, jsonify

from app.database import sync_session
from app.models import Task
from app.services.tasks import reverse_geocode_and_calculate_distances
from app.utils.file_processing import process_file_data


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
        try:
            task_id = uuid4()

            file_data = io.StringIO(file.read().decode('utf-8'))
            points: list = process_file_data(file_data)

            new_task = Task(
                id=task_id,
                status='running',
            )

            try:
                with sync_session() as session:
                    session.add(new_task)
                    session.commit()
            except Exception as e:
                session.rollback()
                raise e

            # local_calc(points, task_id)
            reverse_geocode_and_calculate_distances.apply_async(args=[points, task_id])

            return jsonify({"task_id": task_id, "status": "running"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def local_calc(points, task_id):
    """Util func for testing localy without celery"""
    from app.utils.file_processing import process_geo_data
    from app.data_access.save_results import save_results_to_db
    res = process_geo_data(points)
    save_results_to_db(res, task_id)
