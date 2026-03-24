from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import SleepSession
from datetime import datetime

bp = Blueprint('sleep', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    sessions = SleepSession.query.filter_by(user_id=current_user.id).order_by(SleepSession.sleep_start.desc()).all()
    return render_template('sleep.html', sessions=sessions)


@bp.route('/add', methods=['GET', 'POST'])  # <-- ADD POST HERE
@login_required
def add():
    if request.method == 'POST':
        sleep_start_str = request.form.get('sleep_start')
        sleep_end_str = request.form.get('sleep_end')
        quality = request.form.get('quality', type=int)
        notes = request.form.get('notes')

        # Parse datetime strings
        sleep_start = datetime.fromisoformat(sleep_start_str) if sleep_start_str else None
        sleep_end = datetime.fromisoformat(sleep_end_str) if sleep_end_str else None

        session = SleepSession(
            user_id=current_user.id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            sleep_quality=quality,
            notes=notes
        )
        db.session.add(session)
        db.session.commit()
        flash('Sleep recorded!', 'success')
        return redirect(url_for('sleep.index'))

    # GET request - show form
    return render_template('sleep_add.html')