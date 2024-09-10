from app.data_access.task_manager import save_results_by_task_id


def local_calc(points, task_id):
    """Util func for testing localy without celery"""
    from app.utils.file_processing import process_geo_data

    task_data = process_geo_data(points)
    save_results_by_task_id(task_id=task_id, task_data=task_data)
