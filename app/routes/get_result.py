import json
import uuid

from flask import Blueprint, Response, jsonify

from app.data_access.task_manager import get_all_by_task_id

get_result_bp = Blueprint("get_result", __name__)


@get_result_bp.route("/getResult/<uuid:result_id>", methods=["GET"])
def get_result_route(result_id: uuid.UUID):
    """Get result by task ID endpoint."""
    try:
        result = get_all_by_task_id(result_id)
    except ValueError:
        return jsonify({"error": f"Task {result_id} not found"}), 404

    return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
