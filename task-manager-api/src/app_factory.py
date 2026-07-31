from flask import Flask
from flask_cors import CORS

from config import settings
from infra.database import db
from middlewares.error_handler import register_error_handlers
from utils.helpers import utc_now
from views.category_routes import category_bp
from views.report_routes import report_bp
from views.task_routes import task_bp
from views.user_routes import user_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = settings.SQLALCHEMY_TRACK_MODIFICATIONS

    CORS(app)
    db.init_app(app)

    register_error_handlers(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": str(utc_now())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with app.app_context():
        db.create_all()

    return app
