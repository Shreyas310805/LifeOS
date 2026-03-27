from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('sleep', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    sessions = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('sleep_sessions').where('user_id', '==', current_user.id).order_by('sleep_start', direction=firestore.Query.DESCENDING).stream()]
    return render_template('sleep.html', sessions=sessions)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        db = current_app.config['db']
        db.collection('sleep_sessions').add({
            'user_id': current_user.id,
            'sleep_start': request.form.get('sleep_start'),
            'sleep_end': request.form.get('sleep_end'),
            'sleep_quality': request.form.get('quality', type=int),
            'notes': request.form.get('notes'),
            'recorded_at': datetime.now(timezone.utc)
        })
        flash('Sleep recorded!', 'success')
        return redirect(url_for('sleep.index'))
    return render_template('sleep_add.html')