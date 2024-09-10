import uuid
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoDBRepository:
    """MongoDB Implementation"""

    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client['mydatabase']
        self.tasks_collection = self.db['tasks']

    def create_task(self, task_data: dict) -> uuid.UUID:
        """Create new task."""
        task_id = uuid.uuid4()
        task_data['_id'] = str(task_id)

        try:
            self.tasks_collection.insert_one(task_data)
        except DuplicateKeyError:
            raise ValueError("Task with the same ID already exists.")

        return task_id

    def get_task(self, task_id: uuid.UUID) -> dict:
        """Get task by task_id."""
        task = self.tasks_collection.find_one({"_id": str(task_id)})
        return task

    def update_task(self, task_id: uuid.UUID, task_data: dict):
        """Update task by task_id."""
        task_id_str = str(task_id)
        task = self.get_task(task_id)

        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        # Update the distances
        distances_json = [{'name': link['name'], 'distance': link['distance']} for link in task_data['links']]

        points_entries = [
            {
                'name': point['name'],
                'address': point['address'],
            }
            for point in task_data['points']
        ]

        # Update the task's status? points and distances
        update_result = self.tasks_collection.update_one(
            {"_id": task_id_str},
            {"$set": {"distances": distances_json, "status": "done", "points": points_entries}}
        )
