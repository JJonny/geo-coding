import pytest
from unittest.mock import patch


@pytest.fixture(scope="session")
def app():
    # Patch validate so tests don't require a real .env / running DB
    with patch("app.config.settings.validate"):
        from app import create_app

        application, _ = create_app()
        application.config["TESTING"] = True
        return application


@pytest.fixture
def client(app):
    return app.test_client()
