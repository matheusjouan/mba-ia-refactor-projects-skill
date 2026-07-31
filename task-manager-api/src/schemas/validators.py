from config.settings import (
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)
from utils.helpers import is_valid_color, parse_date, sanitize_string, validate_email


class ValidationError(Exception):
    """Erro de validação de payload de entrada."""


def validar_task(dados, parcial=False):
    resultado = {}

    if "title" in dados or not parcial:
        title = sanitize_string(dados.get("title"))
        if not title:
            raise ValidationError("Título não pode ser vazio")
        if len(title) < MIN_TITLE_LENGTH:
            raise ValidationError("Título muito curto")
        if len(title) > MAX_TITLE_LENGTH:
            raise ValidationError("Título muito longo")
        resultado["title"] = title

    if "description" in dados:
        resultado["description"] = dados["description"]

    if "status" in dados:
        status = dados["status"]
        if status not in VALID_STATUSES:
            raise ValidationError("Status inválido")
        resultado["status"] = status
    elif not parcial:
        resultado["status"] = "pending"

    if "priority" in dados:
        priority = dados["priority"]
        if priority < 1 or priority > 5:
            raise ValidationError("Prioridade deve ser entre 1 e 5")
        resultado["priority"] = priority
    elif not parcial:
        resultado["priority"] = 3

    if "due_date" in dados:
        if dados["due_date"]:
            parsed = parse_date(dados["due_date"])
            if not parsed:
                raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")
            resultado["due_date"] = parsed
        else:
            resultado["due_date"] = None

    if "tags" in dados:
        tags = dados["tags"]
        resultado["tags"] = ",".join(tags) if isinstance(tags, list) else tags

    if "user_id" in dados:
        resultado["user_id"] = dados["user_id"]

    if "category_id" in dados:
        resultado["category_id"] = dados["category_id"]

    return resultado


def validar_usuario(dados, parcial=False):
    resultado = {}

    if "name" in dados or not parcial:
        name = dados.get("name")
        if not name:
            raise ValidationError("Nome é obrigatório")
        resultado["name"] = name

    if "email" in dados or not parcial:
        email = dados.get("email")
        if not email:
            raise ValidationError("Email é obrigatório")
        if not validate_email(email):
            raise ValidationError("Email inválido")
        resultado["email"] = email

    if "password" in dados or not parcial:
        password = dados.get("password")
        if not parcial and not password:
            raise ValidationError("Senha é obrigatória")
        if password and len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha deve ter no mínimo 4 caracteres")
        if password:
            resultado["password"] = password

    if "role" in dados:
        role = dados["role"]
        if role not in VALID_ROLES:
            raise ValidationError("Role inválido")
        resultado["role"] = role
    elif not parcial:
        resultado["role"] = "user"

    if "active" in dados:
        resultado["active"] = dados["active"]

    return resultado


def validar_categoria(dados):
    name = dados.get("name")
    if not name:
        raise ValidationError("Nome é obrigatório")

    color = dados.get("color", "#000000")
    if not is_valid_color(color):
        raise ValidationError("Cor inválida. Use o formato #RRGGBB")

    return {
        "name": name,
        "description": dados.get("description", ""),
        "color": color,
    }
