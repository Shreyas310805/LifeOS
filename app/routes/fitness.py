from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Fitness

bp = Blueprint('fitness', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    activities = Fitness.query.filter_by(user_id=current_user.id).order_by(Fitness.performed_at.desc()).all()
    return render_template('fitness.html', activities=activities)


@bp.route('/add', methods=['GET', 'POST'])  # <-- ADD POST HERE
@login_required
def add():
    if request.method == 'POST':
        activity_type = request.form.get('activity_type')
        duration = request.form.get('duration', type=int)
        calories = request.form.get('calories', type=int)
        intensity = request.form.get('intensity', 'moderate')
        notes = request.form.get('notes')

        workout = Fitness(
            user_id=current_user.id,
            activity_type=activity_type,
            duration_minutes=duration,
            calories_burned=calories,
            intensity=intensity,
            notes=notes
        )
        db.session.add(workout)
        db.session.commit()
        flash('Workout logged!', 'success')
        return redirect(url_for('fitness.index'))

    # GET request - show form
    return render_template('fitness_add.html')