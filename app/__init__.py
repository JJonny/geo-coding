from flask import Flask
from .config import Config
from .routes.calculate_distance import calculate_distance_bp
from .routes.get_result import get_result_bp
from .utils.celery_app import make_celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(calculate_distance_bp, url_prefix='/api')
    app.register_blueprint(get_result_bp, url_prefix='/api')

    # Celery init
    celery = make_celery(app)
    celery.set_default()

    return app, celery
