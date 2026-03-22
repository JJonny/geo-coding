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

    @patch(PATCH_GET_ALL, side_effect=ValueError("not found"))
    def test_unknown_task_returns_404(self, mock_get_all, client):
        task_id = uuid.uuid4()
        response = client.get(f"/api/getResult/{task_id}")
        assert response.status_code == 404
        assert "not found" in response.get_json()["error"].lower()

    @patch(PATCH_GET_ALL)
    def test_running_task_returns_200(self, mock_get_all, client):
        task_id = uuid.uuid4()
        mock_get_all.return_value = make_result(str(task_id), "running")

        response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["task_id"] == str(task_id)
        assert body["status"] == "running"

    @patch(PATCH_GET_ALL)
    def test_done_task_returns_points_and_links(self, mock_get_all, client):
        task_id = uuid.uuid4()
        points = [{"name": "Moscow", "address": "Moscow, Russia"}]
        links = [{"from": "Moscow", "to": "London", "distance": 2500000.0}]
        mock_get_all.return_value = make_result(str(task_id), "done", points=points, links=links)

        response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "done"
        assert body["data"]["points"] == points
        assert body["data"]["links"] == links

    @patch(PATCH_GET_ALL)
    def test_failed_task_returns_200_with_failed_status(self, mock_get_all, client):
        task_id = uuid.uuid4()
        mock_get_all.return_value = make_result(str(task_id), "failed")

        response = client.get(f"/api/getResult/{task_id}")

        assert response.status_code == 200
        assert response.get_json()["status"] == "failed"

    @patch(PATCH_GET_ALL)
    def test_response_is_valid_json(self, mock_get_all, client):
        task_id = uuid.uuid4()
        mock_get_all.return_value = make_result(str(task_id), "done")

        response = client.get(f"/api/getResult/{task_id}")

        assert response.content_type == "application/json"
        assert response.get_json() is not None

    @patch(PATCH_GET_ALL)
    def test_get_all_called_with_correct_task_id(self, mock_get_all, client):
        task_id = uuid.uuid4()
        mock_get_all.return_value = make_result(str(task_id), "done")

        client.get(f"/api/getResult/{task_id}")

        mock_get_all.assert_called_once_with(task_id)

    @patch(PATCH_GET_ALL)
    def test_cyrillic_address_preserved_in_response(self, mock_get_all, client):
        """Non-ASCII characters must survive JSON serialisation."""
        task_id = uuid.uuid4()
        points = [{"name": "Москва", "address": "Москва, Россия"}]
        mock_get_all.return_value = make_result(str(task_id), "done", points=points)

        response = client.get(f"/api/getResult/{task_id}")

        body = response.get_json()
        assert body["data"]["points"][0]["name"] == "Москва"
