import re
from datetime import datetime, timezone


def utc_now():
    """UTC "agora", mantido sem timezone (naive) para continuar comparável com
    as colunas DateTime existentes, que também são naive."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email))


def sanitize_string(value):
    return value.strip() if value else value


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except (TypeError, ValueError):
        try:
            return datetime.strptime(date_string, "%d/%m/%Y")
        except (TypeError, ValueError):
            return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color[0] == "#")
