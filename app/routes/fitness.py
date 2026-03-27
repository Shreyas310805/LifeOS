from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('fitness', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    activities = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('fitness').where('user_id', '==', current_user.id).order_by('performed_at', direction=firestore.Query.DESCENDING).stream()]
    return render_template('fitness.html', activities=activities)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        db = current_app.config['db']
        db.collection('fitness').add({
            'user_id': current_user.id,
            'activity_type': request.form.get('activity_type'),
            'duration_minutes': request.form.get('duration', type=int),
            'calories_burned': request.form.get('calories', type=int),
            'intensity': request.form.get('intensity', 'moderate'),
            'notes': request.form.get('notes'),
            'performed_at': datetime.now(timezone.utc)
        })
        flash('Workout logged!', 'success')
        return redirect(url_for('fitness.index'))
    return render_template('fitness_add.html')