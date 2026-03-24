from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import HealthMetric

bp = Blueprint('health', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    metrics = HealthMetric.query.filter_by(user_id=current_user.id).order_by(HealthMetric.recorded_at.desc()).all()
    return render_template('health.html', metrics=metrics)


@bp.route('/add', methods=['GET', 'POST'])  # <-- ADD POST HERE
@login_required
def add():
    if request.method == 'POST':
        metric_type = request.form.get('metric_type')
        value = request.form.get('value', type=float)
        unit = request.form.get('unit')
        notes = request.form.get('notes')

        metric = HealthMetric(
            user_id=current_user.id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            notes=notes
        )
        db.session.add(metric)
        db.session.commit()
        flash('Health metric recorded!', 'success')
        return redirect(url_for('health.index'))

    # GET request - show form
    return render_template('health_add.html')


@bp.route('/api/metrics', methods=['GET'])
@login_required
def api_metrics():
    metrics = HealthMetric.query.filter_by(user_id=current_user.id).all()
    return jsonify([m.to_dict() for m in metrics])