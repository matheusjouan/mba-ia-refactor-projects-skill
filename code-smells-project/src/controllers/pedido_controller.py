from flask import jsonify, request

from models import pedido_model
from schemas.validators import validar_pedido, validar_status_pedido
from services import pedido_service


def criar_pedido():
    usuario_id, itens = validar_pedido(request.get_json())
    resultado = pedido_service.criar_pedido(usuario_id, itens)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.get_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json() or {}
    novo_status = validar_status_pedido(dados.get("status", ""))
    pedido_service.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
