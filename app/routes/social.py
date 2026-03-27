from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('social', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    posts = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('social').order_by('created_at', direction=firestore.Query.DESCENDING).stream()]
    return render_template('social.html', posts=posts)

@bp.route('/post', methods=['POST'])
@login_required
def post():
    db = current_app.config['db']
    db.collection('social').add({
        'user_id': current_user.id,
        'content': request.form.get('content'),
        'post_type': request.form.get('post_type', 'update'),
        'created_at': datetime.now(timezone.utc)
    })
    flash('Post shared!', 'success')
    return redirect(url_for('social.index'))