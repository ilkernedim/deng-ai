# __init__.py - Modul E: uygulama fabrikasi
from flask import Flask
from flask_cors import CORS

from config import get_config
from .database import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.json.ensure_ascii = False
    CORS(app, origins=app.config["CORS_ORIGINS"])
    init_db(app)

    from .routes import sayfalar, api
    app.register_blueprint(sayfalar)
    app.register_blueprint(api)
    return app
