from flask import jsonify, request
from sqlalchemy.orm import joinedload

from infra.database import db
from models.category import Category
from models.task import Task
from models.user import User
from schemas.validators import validar_task
from utils.helpers import calculate_percentage


def get_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return jsonify([t.to_dict() for t in tasks]), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    return jsonify(task.to_dict()), 200


def create_task():
    dados = validar_task(request.get_json() or {})

    if dados.get("user_id") and not db.session.get(User, dados["user_id"]):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if dados.get("category_id") and not db.session.get(Category, dados["category_id"]):
        return jsonify({"error": "Categoria não encontrada"}), 404

    task = Task(**dados)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    dados = validar_task(request.get_json() or {}, parcial=True)

    if dados.get("user_id") and not db.session.get(User, dados["user_id"]):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if dados.get("category_id") and not db.session.get(Category, dados["category_id"]):
        return jsonify({"error": "Categoria não encontrada"}), 404

    for campo, valor in dados.items():
        setattr(task, campo, valor)

    db.session.commit()
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks_query = Task.query.options(joinedload(Task.user), joinedload(Task.category))
    if query:
        tasks_query = tasks_query.filter(
            db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%"))
        )
    if status:
        tasks_query = tasks_query.filter(Task.status == status)
    if priority:
        tasks_query = tasks_query.filter(Task.priority == int(priority))
    if user_id:
        tasks_query = tasks_query.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in tasks_query.all()]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()
    overdue = Task.query.filter(Task.overdue_filter()).count()

    return jsonify({
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue,
        "completion_rate": calculate_percentage(done, total),
    }), 200
