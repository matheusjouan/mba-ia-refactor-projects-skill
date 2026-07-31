from flask import current_app, jsonify

from schemas.validators import ValidationError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(erro):
        return jsonify({"error": str(erro)}), 400

    @app.errorhandler(404)
    def handle_not_found(_erro):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(erro):
        current_app.logger.exception("Erro não tratado: %s", erro)
        return jsonify({"error": "Erro interno"}), 500
