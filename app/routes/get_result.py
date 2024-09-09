import json

from flask import Blueprint, Response

from app.data_access.task_manager import get_all_by_task_id

get_result_bp = Blueprint('get_result', __name__)


@get_result_bp.route('/getResult/<uuid:result_id>', methods=['GET'])
def get_result_route(result_id):
    """Get result by task ID endpoint."""
    result = get_all_by_task_id(result_id)
    result = json.dumps(result, ensure_ascii=False)

    return Response(result, mimetype='application/json')
