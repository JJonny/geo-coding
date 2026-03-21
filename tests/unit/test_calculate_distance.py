import io
import uuid
from unittest.mock import MagicMock, patch

import pytest


def make_csv(*rows: tuple) -> bytes:
    """Build a minimal CSV bytes payload with header row."""
    lines = ["name,lat,lon"] + [f"{name},{lat},{lon}" for name, lat, lon in rows]
    return "\n".join(lines).encode("utf-8")


def post_csv(client, content: bytes, filename: str = "points.csv"):
    return client.post(
        "/api/calculateDistance",
        data={"file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


# ---------------------------------------------------------------------------
# Request validation – no DB/Celery interaction needed
# ---------------------------------------------------------------------------


class TestRequestValidation:
    def test_no_file_part_returns_400(self, client):
        response = client.post("/api/calculateDistance")
        assert response.status_code == 400
        assert "No file part" in response.get_json()["error"]

    def test_empty_filename_returns_400(self, client):
        response = client.post(
            "/api/calculateDistance",
            data={"file": (io.BytesIO(b""), "")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        assert "No selected file" in response.get_json()["error"]

    def test_file_exceeds_size_limit_returns_400(self, client):
        large = b"x" * (11 * 1024 * 1024)  # 11 MB > 10 MB limit
        response = post_csv(client, large)
        assert response.status_code == 400
        assert "exceeds maximum" in response.get_json()["error"]

    def test_non_utf8_file_returns_400(self, client):
        response = post_csv(client, b"\xff\xfe bad bytes")
        assert response.status_code == 400
        assert "UTF-8" in response.get_json()["error"]

    def test_header_only_csv_returns_400(self, client):
        response = post_csv(client, b"name,lat,lon\n")
        assert response.status_code == 400
        assert "No valid coordinate rows" in response.get_json()["error"]

    def test_all_rows_out_of_range_returns_400(self, client):
        csv = make_csv(("loc1", 999, 0), ("loc2", 0, 999))
        response = post_csv(client, csv)
        assert response.status_code == 400
        assert "No valid coordinate rows" in response.get_json()["error"]

    def test_all_rows_malformed_returns_400(self, client):
        content = b"name,lat,lon\nbad,not_a_number,also_bad\n"
        response = post_csv(client, content)
        assert response.status_code == 400
        assert "No valid coordinate rows" in response.get_json()["error"]

    def test_rows_missing_columns_returns_400(self, client):
        content = b"name,lat,lon\nonly_two_columns,55.75\n"
        response = post_csv(client, content)
        assert response.status_code == 400
        assert "No valid coordinate rows" in response.get_json()["error"]


# ---------------------------------------------------------------------------
# Happy-path – DB and Celery are mocked
# ---------------------------------------------------------------------------


PATCH_SESSION = "app.routes.calculate_distance.sync_session"
PATCH_FACTORY = "app.routes.calculate_distance.RepositoryFactory"
PATCH_TASK = "app.routes.calculate_distance.reverse_geocode_and_calculate_distances"


def _make_mock_repo(task_id: str) -> MagicMock:
    repo = MagicMock()
    repo.create_task.return_value = task_id
    return repo


class TestSuccessfulRequest:
    def test_returns_200_with_task_id(self, client):
        task_id = str(uuid.uuid4())
        csv = make_csv(("Moscow", 55.75, 37.62), ("London", 51.50, -0.12))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK) as mock_task:

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)

            response = post_csv(client, csv)

        assert response.status_code == 200
        body = response.get_json()
        assert body["task_id"] == task_id
        assert body["status"] == "running"

    def test_celery_task_is_enqueued(self, client):
        task_id = str(uuid.uuid4())
        csv = make_csv(("Moscow", 55.75, 37.62))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK) as mock_task:

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)
            post_csv(client, csv)

        mock_task.apply_async.assert_called_once()

    def test_celery_task_receives_correct_task_id(self, client):
        task_id = str(uuid.uuid4())
        csv = make_csv(("Moscow", 55.75, 37.62))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK) as mock_task:

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)
            post_csv(client, csv)

        args_passed = mock_task.apply_async.call_args[1]["args"]
        assert args_passed[1] == task_id  # second arg is task_id

    def test_celery_task_receives_parsed_points(self, client):
        task_id = str(uuid.uuid4())
        csv = make_csv(("Moscow", 55.75, 37.62), ("London", 51.50, -0.12))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK) as mock_task:

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)
            post_csv(client, csv)

        points_passed = mock_task.apply_async.call_args[1]["args"][0]
        assert len(points_passed) == 2
        assert points_passed[0].name == "Moscow"
        assert points_passed[0].lat == 55.75
        assert points_passed[0].lon == 37.62

    def test_repository_create_task_called_with_running_status(self, client):
        from app.models import TaskStatus

        task_id = str(uuid.uuid4())
        csv = make_csv(("Moscow", 55.75, 37.62))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK):

            mock_repo = _make_mock_repo(task_id)
            mock_factory.return_value.get_repository.return_value = mock_repo
            post_csv(client, csv)

        mock_repo.create_task.assert_called_once_with({"status": TaskStatus.RUNNING})

    def test_valid_boundary_coordinates_accepted(self, client):
        """Coordinates on exact boundary values (-90/90 lat, -180/180 lon) must be accepted."""
        task_id = str(uuid.uuid4())
        csv = make_csv(("NorthPole", 90.0, 0.0), ("DateLine", 0.0, 180.0))

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK):

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)
            response = post_csv(client, csv)

        assert response.status_code == 200

    def test_mixed_valid_and_invalid_rows_only_valid_forwarded(self, client):
        task_id = str(uuid.uuid4())
        # Two valid rows + one row out of range
        content = b"name,lat,lon\nMoscow,55.75,37.62\nBad,999,0\nLondon,51.50,-0.12\n"

        with patch(PATCH_SESSION), \
             patch(PATCH_FACTORY) as mock_factory, \
             patch(PATCH_TASK) as mock_task:

            mock_factory.return_value.get_repository.return_value = _make_mock_repo(task_id)
            response = post_csv(client, content)

        assert response.status_code == 200
        points_passed = mock_task.apply_async.call_args[1]["args"][0]
        assert len(points_passed) == 2
        assert all(p.name in ("Moscow", "London") for p in points_passed)
