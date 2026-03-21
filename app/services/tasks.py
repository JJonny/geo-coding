import logging
import uuid

from celery import shared_task

from app.data_access.models.models import Distance, Point, PointAddress
from app.data_access.task_manager import save_results_by_task_id, set_task_failed
from app.utils.file_processing import process_geo_data

logger = logging.getLogger(__name__)


@shared_task
def reverse_geocode_and_calculate_distances(points: list[Point], task_id: uuid.UUID):
    """Celery task for calculate distances and addresses for points."""
    try:
        points = [Point(*p) if not isinstance(p, Point) else p for p in points]
        task_data: dict[str, list[Distance | PointAddress]] = process_geo_data(points)
        save_results_by_task_id(task_id=task_id, task_data=task_data)
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        set_task_failed(task_id=task_id)
