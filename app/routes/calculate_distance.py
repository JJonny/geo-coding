import io
import logging

from flask import Blueprint, request, jsonify, current_app

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
        repository_factory = RepositoryFactory(app=current_app)

        repository = repository_factory.get_repository()
        task_data = {"status": "running"}
        task_id = repository.create_task(task_data)

        file_data = io.StringIO(file.read().decode('utf-8'))
        points: list = process_file_data(file_data)

        # from app.utils.local_calculation import local_calc
        # local_calc(points, task_id)
        reverse_geocode_and_calculate_distances.apply_async(args=[points, task_id])

        return jsonify({"task_id": task_id, "status": "running"}), 200


