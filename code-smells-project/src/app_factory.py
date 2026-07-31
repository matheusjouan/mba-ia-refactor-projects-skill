from flask import Flask
from flask_cors import CORS

from config import settings
from infra import database
from middlewares.error_handler import register_error_handlers
from views.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    app.teardown_appcontext(database.close_db)

    with app.app_context():
        db = database.get_db()
        database.init_schema(db)
        database.seed_if_empty(db)

    register_error_handlers(app)
    register_routes(app)

    return app
