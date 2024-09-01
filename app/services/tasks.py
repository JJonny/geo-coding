import logging

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from app.utils.file_processing import process_geo_data
from app.data_access.save_results import save_results_to_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@shared_task(base=AbortableTask)
def reverse_geocode_and_calculate_distances(points, task_id):
    try:
        res = process_geo_data(points)
        save_results_to_db(res, task_id)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
