from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('tasks', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    tasks = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('tasks').where('user_id', '==', current_user.id).order_by('created_at', direction=firestore.Query.DESCENDING).stream()]
    return render_template('tasks.html', tasks=tasks)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        db = current_app.config['db']
        db.collection('tasks').add({
            'user_id': current_user.id,
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'category': request.form.get('category', 'general'),
            'priority': request.form.get('priority', 'medium'),
            'status': 'pending',
            'created_at': datetime.now(timezone.utc)
        })
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.index'))
    return render_template('tasks_add.html')

@bp.route('/complete/<id>', methods=['POST'])
@login_required
def complete(id):
    db = current_app.config['db']
    task_ref = db.collection('tasks').document(id)
    task = task_ref.get().to_dict()
    if not task or task.get('user_id') != current_user.id:
        flash('Unauthorized', 'error')
    else:
        task_ref.update({'status': 'completed', 'completed_at': datetime.now(timezone.utc)})
        flash('Task completed!', 'success')
    return redirect(url_for('tasks.index'))

@bp.route('/delete/<id>', methods=['POST'])
@login_required
def delete(id):
    db = current_app.config['db']
    task_ref = db.collection('tasks').document(id)
    task = task_ref.get().to_dict()
    if not task or task.get('user_id') != current_user.id:
        flash('Unauthorized', 'error')
    else:
        task_ref.delete()
        flash('Task deleted!', 'success')
    return redirect(url_for('tasks.index'))