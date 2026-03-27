from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone

bp = Blueprint('nutrition', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    db = current_app.config['db']
    meals = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('meals').where('user_id', '==', current_user.id).order_by('logged_at', direction=firestore.Query.DESCENDING).stream()]
    return render_template('nutrition.html', meals=meals)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        db = current_app.config['db']
        db.collection('meals').add({
            'user_id': current_user.id,
            'meal_name': request.form.get('meal_name'),
            'meal_type': request.form.get('meal_type'),
            'total_calories': request.form.get('calories', type=float),
            'protein_g': request.form.get('protein', type=float),
            'carbs_g': request.form.get('carbs', type=float),
            'fat_g': request.form.get('fat', type=float),
            'logged_at': datetime.now(timezone.utc)
        })
        flash('Meal logged!', 'success')
        return redirect(url_for('nutrition.index'))
    return render_template('nutrition_add.html')