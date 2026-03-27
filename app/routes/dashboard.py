from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from google.cloud import firestore

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    db = current_app.config['db']
    recent_metrics = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('health_metrics').where('user_id', '==', current_user.id).order_by('recorded_at', direction=firestore.Query.DESCENDING).limit(5).stream()]
    pending_tasks = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('tasks').where('user_id', '==', current_user.id).where('status', '==', 'pending').order_by('due_date', direction=firestore.Query.ASCENDING).limit(5).stream()]
    recent_workouts = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('fitness').where('user_id', '==', current_user.id).order_by('performed_at', direction=firestore.Query.DESCENDING).limit(3).stream()]
    
    return render_template('dashboard.html', user=current_user, metrics=recent_metrics, tasks=pending_tasks, workouts=recent_workouts)