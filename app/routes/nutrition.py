from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Meal

bp = Blueprint('nutrition', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.logged_at.desc()).all()
    return render_template('nutrition.html', meals=meals)


@bp.route('/add', methods=['GET', 'POST'])  # <-- ADD POST HERE
@login_required
def add():
    if request.method == 'POST':
        meal_name = request.form.get('meal_name')
        meal_type = request.form.get('meal_type')
        calories = request.form.get('calories', type=float)
        protein = request.form.get('protein', type=float)
        carbs = request.form.get('carbs', type=float)
        fat = request.form.get('fat', type=float)

        meal = Meal(
            user_id=current_user.id,
            meal_name=meal_name,
            meal_type=meal_type,
            total_calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat
        )
        db.session.add(meal)
        db.session.commit()
        flash('Meal logged!', 'success')
        return redirect(url_for('nutrition.index'))

    # GET request - show form
    return render_template('nutrition_add.html')