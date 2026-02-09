from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Task

bp = Blueprint('tasks', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=tasks)


@bp.route('/add', methods=['GET', 'POST'])  # <-- ADD POST HERE
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category', 'general')
        priority = request.form.get('priority', 'medium')

        task = Task(
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            priority=priority
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.index'))

    # GET request - show form
    return render_template('tasks_add.html')  # Create this template


@bp.route('/complete/<int:id>', methods=['POST'])  # <-- CHANGE TO POST
@login_required
def complete(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('tasks.index'))

    task.status = 'completed'
    task.completed_at = db.func.now()
    db.session.commit()
    flash('Task completed!', 'success')
    return redirect(url_for('tasks.index'))


@bp.route('/delete/<int:id>', methods=['POST'])  # <-- CHANGE TO POST
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('tasks.index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('tasks.index'))