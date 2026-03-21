import uuid
from unittest.mock import patch

import pytest


PATCH_GET_ALL = "app.routes.get_result.get_all_by_task_id"


def make_result(task_id: str, status: str, points=None, links=None) -> dict:
    return {
        "task_id": task_id,
        "status": status,
        "data": {
            "points": points or [],
            "links": links,
        },
    }


class TestGetResultRoute:
    def test_invalid_uuid_returns_404(self, client):
        response = client.get("/api/getResult/not-a-uuid")
        assert response.status_code == 404

    def test_unknown_task_returns_404(self, client):
        task_id = uuid.uuid4()
        with patch(PATCH_GET_ALL, side_effect=ValueError("not found")):
            response = client.get(f"/api/getResult/{task_id}")
        assert response.status_code == 404
        assert "not found" in response.get_json()["error"].lower()

    def test_running_task_returns_200(self, client):
        task_id = uuid.uuid4()
        result = make_result(str(task_id), "running")

        with patch(PATCH_GET_ALL, return_value=result):
            response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["task_id"] == str(task_id)
        assert body["status"] == "running"

    def test_done_task_returns_points_and_links(self, client):
        task_id = uuid.uuid4()
        points = [{"name": "Moscow", "address": "Moscow, Russia"}]
        links = [{"from": "Moscow", "to": "London", "distance": 2500000.0}]
        result = make_result(str(task_id), "done", points=points, links=links)

        with patch(PATCH_GET_ALL, return_value=result):
            response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "done"
        assert body["data"]["points"] == points
        assert body["data"]["links"] == links

    def test_failed_task_returns_200_with_failed_status(self, client):
        task_id = uuid.uuid4()
        result = make_result(str(task_id), "failed")

        with patch(PATCH_GET_ALL, return_value=result):
            response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        assert response.get_json()["status"] == "failed"

    def test_response_is_valid_json(self, client):
        task_id = uuid.uuid4()
        result = make_result(str(task_id), "done")

        with patch(PATCH_GET_ALL, return_value=result):
            response = client.get(f"/api/getResult/{task_id}")

        assert response.content_type == "application/json"
        assert response.get_json() is not None

    def test_get_all_called_with_correct_task_id(self, client):
        task_id = uuid.uuid4()
        result = make_result(str(task_id), "done")

        with patch(PATCH_GET_ALL, return_value=result) as mock_get:
            client.get(f"/api/getResult/{task_id}")

        mock_get.assert_called_once_with(task_id)

    def test_cyrillic_address_preserved_in_response(self, client):
        """Non-ASCII characters must survive JSON serialisation."""
        task_id = uuid.uuid4()
        points = [{"name": "Москва", "address": "Москва, Россия"}]
        result = make_result(str(task_id), "done", points=points)

        with patch(PATCH_GET_ALL, return_value=result):
            response = client.get(f"/api/getResult/{task_id}")

        body = response.get_json()
        assert body["data"]["points"][0]["name"] == "Москва"
