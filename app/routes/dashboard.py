from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import HealthMetric, Task, Fitness

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    recent_metrics = HealthMetric.query.filter_by(user_id=current_user.id) \
        .order_by(HealthMetric.recorded_at.desc()).limit(5).all()

    pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending') \
        .order_by(Task.due_date.asc()).limit(5).all()

    recent_workouts = Fitness.query.filter_by(user_id=current_user.id) \
        .order_by(Fitness.performed_at.desc()).limit(3).all()

    return render_template('dashboard.html',
                           user=current_user,
                           metrics=recent_metrics,
                           tasks=pending_tasks,
                           workouts=recent_workouts)