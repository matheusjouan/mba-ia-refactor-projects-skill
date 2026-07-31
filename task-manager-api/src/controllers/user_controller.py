from flask import jsonify, request
from sqlalchemy import func

from infra.database import db
from models.task import Task
from models.user import User
from schemas.validators import validar_usuario


def get_users():
    contagens = dict(
        db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
    )
    resultado = []
    for usuario in User.query.all():
        dados = usuario.to_dict()
        dados["task_count"] = contagens.get(usuario.id, 0)
        resultado.append(dados)
    return jsonify(resultado), 200


def get_user(user_id):
    usuario = db.session.get(User, user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    dados = usuario.to_dict()
    dados["tasks"] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return jsonify(dados), 200


def create_user():
    dados = validar_usuario(request.get_json() or {})
    if User.query.filter_by(email=dados["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    usuario = User(name=dados["name"], email=dados["email"], role=dados["role"])
    usuario.set_password(dados["password"])
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


def update_user(user_id):
    usuario = db.session.get(User, user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    dados = validar_usuario(request.get_json() or {}, parcial=True)

    if "email" in dados:
        existente = User.query.filter_by(email=dados["email"]).first()
        if existente and existente.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        usuario.email = dados["email"]
    if "name" in dados:
        usuario.name = dados["name"]
    if "password" in dados:
        usuario.set_password(dados["password"])
    if "role" in dados:
        usuario.role = dados["role"]
    if "active" in dados:
        usuario.active = dados["active"]

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


def delete_user(user_id):
    usuario = db.session.get(User, user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    usuario = db.session.get(User, user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


def login():
    dados = request.get_json() or {}
    email = dados.get("email")
    password = dados.get("password")

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    usuario = User.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not usuario.active:
        return jsonify({"error": "Usuário inativo"}), 403

    return jsonify({
        "message": "Login realizado com sucesso",
        "user": usuario.to_dict(),
        "token": f"fake-jwt-token-{usuario.id}",
    }), 200
