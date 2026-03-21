import io
import logging
import uuid

from flask import Blueprint, current_app, jsonify, request

from app.database import sync_session
from app.data_access.models.models import Point
from app.data_access.repositories.repository_factory import RepositoryFactory
from app.models import TaskStatus
from app.services.tasks import reverse_geocode_and_calculate_distances
from app.utils.file_processing import process_file_data

logger = logging.getLogger(__name__)
calculate_distance_bp = Blueprint("calculate_distance", __name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@calculate_distance_bp.route("/calculateDistance", methods=["POST"])
def calculate_distance_route():
    """Calculate distance endpoint."""

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    raw = file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB"}), 400

    try:
        file_data = io.StringIO(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return jsonify({"error": "File must be UTF-8 encoded text"}), 400

    try:
        points: list[Point] = process_file_data(file_data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not points:
        return jsonify({"error": "No valid coordinate rows found in the file"}), 400

    with sync_session() as session:
        repository_factory = RepositoryFactory(app=current_app)
        repository = repository_factory.get_repository(session)
        task_id = repository.create_task({"status": TaskStatus.RUNNING})

    reverse_geocode_and_calculate_distances.apply_async(args=[points, task_id])

    return jsonify({"task_id": task_id, "status": TaskStatus.RUNNING.value}), 200
