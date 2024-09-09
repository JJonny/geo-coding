import logging

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from app.utils.file_processing import process_geo_data
from app.data_access.task_manager import save_results_by_task_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@shared_task(base=AbortableTask)
def reverse_geocode_and_calculate_distances(points, task_id):
    """Celery task for calculate distances and addresses for points."""
    try:
        task_data = process_geo_data(points)
        save_results_by_task_id(task_id=task_id, task_data=task_data)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
