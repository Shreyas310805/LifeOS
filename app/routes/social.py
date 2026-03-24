from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Social

bp = Blueprint('social', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    posts = Social.query.order_by(Social.created_at.desc()).all()
    return render_template('social.html', posts=posts)


@bp.route('/post', methods=['POST'])  # <-- KEEP AS POST
@login_required
def post():
    content = request.form.get('content')
    post_type = request.form.get('post_type', 'update')

    social_post = Social(
        user_id=current_user.id,
        content=content,
        post_type=post_type
    )
    db.session.add(social_post)
    db.session.commit()
    flash('Post shared!', 'success')
    return redirect(url_for('social.index'))