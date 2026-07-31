from datetime import timedelta

from flask import jsonify
from sqlalchemy import func

from infra.database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utc_now


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    status_counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    priority_counts = dict(db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all())

    overdue_tasks = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < utc_now(),
        Task.status.notin_(["done", "cancelled"]),
    ).all()

    seven_days_ago = utc_now() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()

    task_counts_by_user = dict(db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all())
    done_counts_by_user = dict(
        db.session.query(Task.user_id, func.count(Task.id))
        .filter(Task.status == "done")
        .group_by(Task.user_id)
        .all()
    )

    user_stats = []
    for usuario in User.query.all():
        total = task_counts_by_user.get(usuario.id, 0)
        completed = done_counts_by_user.get(usuario.id, 0)
        user_stats.append({
            "user_id": usuario.id,
            "user_name": usuario.name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": calculate_percentage(completed, total),
        })

    return jsonify({
        "generated_at": str(utc_now()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": status_counts.get("done", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
        "tasks_by_priority": {
            "critical": priority_counts.get(1, 0),
            "high": priority_counts.get(2, 0),
            "medium": priority_counts.get(3, 0),
            "low": priority_counts.get(4, 0),
            "minimal": priority_counts.get(5, 0),
        },
        "overdue": {
            "count": len(overdue_tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "due_date": str(t.due_date),
                    "days_overdue": (utc_now() - t.due_date).days,
                }
                for t in overdue_tasks
            ],
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }), 200


def user_report(user_id):
    usuario = db.session.get(User, user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == "done")
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    cancelled = sum(1 for t in tasks if t.status == "cancelled")
    high_priority = sum(1 for t in tasks if t.priority <= 2)
    overdue = sum(1 for t in tasks if t.is_overdue())

    return jsonify({
        "user": {"id": usuario.id, "name": usuario.name, "email": usuario.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(done, total),
        },
    }), 200
