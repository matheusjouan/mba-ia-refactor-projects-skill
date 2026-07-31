import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-default")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
