from flask import jsonify, request
from sqlalchemy import func

from infra.database import db
from models.category import Category
from models.task import Task
from schemas.validators import validar_categoria


def get_categories():
    contagens = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )
    resultado = []
    for categoria in Category.query.all():
        dados = categoria.to_dict()
        dados["task_count"] = contagens.get(categoria.id, 0)
        resultado.append(dados)
    return jsonify(resultado), 200


def create_category():
    dados = validar_categoria(request.get_json() or {})
    categoria = Category(**dados)
    db.session.add(categoria)
    db.session.commit()
    return jsonify(categoria.to_dict()), 201


def update_category(cat_id):
    categoria = db.session.get(Category, cat_id)
    if not categoria:
        return jsonify({"error": "Categoria não encontrada"}), 404

    dados = request.get_json() or {}
    if "name" in dados:
        categoria.name = dados["name"]
    if "description" in dados:
        categoria.description = dados["description"]
    if "color" in dados:
        categoria.color = dados["color"]

    db.session.commit()
    return jsonify(categoria.to_dict()), 200


def delete_category(cat_id):
    categoria = db.session.get(Category, cat_id)
    if not categoria:
        return jsonify({"error": "Categoria não encontrada"}), 404
    db.session.delete(categoria)
    db.session.commit()
    return jsonify({"message": "Categoria deletada"}), 200
