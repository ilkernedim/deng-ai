from flask import Flask
from flask_cors import CORS

from config import get_config
from .database import init_db


# uygulamayi kuran fonksiyon, run.py bunu cagiriyor
def create_app():
    app = Flask(__name__)

    app.config.from_object(get_config())
    # turkce karakterler json cevabinda bozuk gorunmesin diye
    app.json.ensure_ascii = False

    # wix sitesi baska adreste oldugu icin istek atabilmesi lazim
    CORS(app)

    init_db(app)

    # sayfalar ve api yollari ayri gruplarda
    from .routes import sayfalar, api
    app.register_blueprint(sayfalar)
    app.register_blueprint(api)

    return app
