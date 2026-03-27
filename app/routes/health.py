from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('health', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    metrics = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('health_metrics').where('user_id', '==', current_user.id).order_by('recorded_at', direction=firestore.Query.DESCENDING).stream()]
    return render_template('health.html', metrics=metrics)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        db = current_app.config['db']
        db.collection('health_metrics').add({
            'user_id': current_user.id,
            'metric_type': request.form.get('metric_type'),
            'value': request.form.get('value', type=float),
            'unit': request.form.get('unit'),
            'notes': request.form.get('notes'),
            'recorded_at': datetime.now(timezone.utc)
        })
        flash('Health metric recorded!', 'success')
        return redirect(url_for('health.index'))
    return render_template('health_add.html')

@bp.route('/api/metrics', methods=['GET'])
@login_required
def api_metrics():
    db = current_app.config['db']
    metrics = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('health_metrics').where('user_id', '==', current_user.id).stream()]
    return jsonify(metrics)