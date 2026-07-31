from flask import jsonify, request

from models import usuario_model
from schemas.validators import validar_usuario
from services import auth_service


def listar_usuarios():
    usuarios = [usuario_model.sanitizar(u) for u in usuario_model.get_todos()]
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_por_id(usuario_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify({"dados": usuario_model.sanitizar(usuario), "sucesso": True}), 200


def criar_usuario():
    dados = validar_usuario(request.get_json())
    senha_hash = auth_service.hash_senha(dados["senha"])
    usuario_id = usuario_model.criar(dados["nome"], dados["email"], senha_hash)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json() or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = auth_service.autenticar(email, senha)
    if not usuario:
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

    return jsonify({"dados": usuario_model.sanitizar(usuario), "sucesso": True, "mensagem": "Login OK"}), 200
