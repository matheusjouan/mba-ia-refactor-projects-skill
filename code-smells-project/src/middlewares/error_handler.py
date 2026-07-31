from functools import wraps

from flask import current_app, jsonify, request

from config import settings
from schemas.validators import ValidationError
from services.pedido_service import PedidoError


def require_admin_token(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header != f"Bearer {settings.ADMIN_TOKEN}":
            return jsonify({"erro": "Não autorizado", "sucesso": False}), 401
        return view(*args, **kwargs)

    return wrapped


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(erro):
        return jsonify({"erro": str(erro), "sucesso": False}), 400

    @app.errorhandler(PedidoError)
    def handle_pedido_error(erro):
        return jsonify({"erro": str(erro), "sucesso": False}), 400

    @app.errorhandler(404)
    def handle_not_found(_erro):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(erro):
        current_app.logger.exception("Erro não tratado: %s", erro)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
