from flask import Flask
from flask_cors import CORS

from pymongo import MongoClient

from app.config import Config
from app.routes.calculate_distance import calculate_distance_bp
from app.routes.get_result import get_result_bp
from app.swagger import swagger_ui_blueprint
from app.utils.celery_app import make_celery


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    if app.config['MONGO']:
        app.mongo_client = MongoClient(app.config['MONGO_URL'])

    app.register_blueprint(calculate_distance_bp, url_prefix='/api')
    app.register_blueprint(get_result_bp, url_prefix='/api')

    # Celery init
    celery = make_celery(app)
    celery.set_default()

    app.register_blueprint(swagger_ui_blueprint, url_prefix='/docs')

    return app, celery
