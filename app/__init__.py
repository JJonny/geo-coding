from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes.calculate_distance import calculate_distance_bp
from .routes.get_result import get_result_bp
from .swagger import swagger_ui_blueprint
from .utils.celery_app import make_celery


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    app.register_blueprint(calculate_distance_bp, url_prefix='/api')
    app.register_blueprint(get_result_bp, url_prefix='/api')

    # Celery init
    celery = make_celery(app)
    celery.set_default()

    app.register_blueprint(swagger_ui_blueprint, url_prefix='/docs')

    return app, celery
