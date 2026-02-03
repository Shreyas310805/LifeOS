import builtins
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifeos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# PASTE YOUR API KEY HERE
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)

# --- DATABASE MODELS ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    xp = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="Shreyas")
    level = db.Column(db.Integer, default=1)
    total_xp = db.Column(db.Integer, default=0)

# --- AI HELPER ---
# REPLACE THE 'decide_points_with_ai' FUNCTION IN app.py WITH THIS:

def decide_points_with_ai(task_description):
    try:
        # We use 'gemini-1.5-flash' as it is faster and free-tier friendly
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"You are the LifeOS Game Master. Assess the difficulty of this task: '{task_description}'. "
            "Reply with ONLY a single integer number between 10 (easy) and 100 (hard). "
            "Examples: 'Wash spoon' -> 10, 'Run marathon' -> 100. "
            "Do not write any text, just the number."
        )
        response = model.generate_content(prompt)
        print(f"AI Thought: {response.text}") 
        return int(response.text.strip())
    except: # <--- CHANGED THIS LINE (Removed 'Exception as e')
        print("AI ERROR: Could not connect to Gemini.")
        return 10
# --- ROUTES ---

@app.route('/')
def dashboard():
    user = User.query.first()
    if not user:
        user = User(name="Shreyas", level=1, total_xp=0)
        db.session.add(user)
        db.session.commit()
        
    tasks = Task.query.all()
    completed_tasks = len([t for t in tasks if t.status == "Done"])
    total_tasks = len(tasks) if len(tasks) > 0 else 1
    task_percent = int((completed_tasks / total_tasks) * 100)

    return render_template('dashboard.html', page='dashboard', user=user, tasks=tasks, task_percent=task_percent)

# --- NEW: THESE WERE MISSING AND CAUSED THE ERROR ---
@app.route('/tasks')
def tasks():
    user = User.query.first()
    all_tasks = Task.query.all()
    return render_template('tasks.html', page='tasks', user=user, tasks=all_tasks)

@app.route('/fitness')
def fitness():
    user = User.query.first()
    return render_template('fitness.html', page='fitness', user=user)

@app.route('/social')
def social():
    user = User.query.first()
    return render_template('social.html', page='social', user=user)
# ----------------------------------------------------

@app.route('/add_task', methods=['POST'])
def add_task():
    task_title = request.form.get('task_name')
    category = request.form.get('category')
    ai_points = decide_points_with_ai(task_title)
    
    new_task = Task(title=task_title, category=category, xp=ai_points)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    user = User.query.first()
    if task and task.status == "Pending":
        task.status = "Done"
        user.total_xp += task.xp
        user.level = 1 + (user.total_xp // 500)
        db.session.commit()
    return redirect(url_for('dashboard'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)