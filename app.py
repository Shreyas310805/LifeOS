import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from google import genai

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifeos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- YOUR API KEY ---
GOOGLE_API_KEY = ""

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

# --- AI HELPER FUNCTION ---
def decide_points_with_ai(task_description):
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        prompt = (
            f"You are the LifeOS Game Master.\n"
            f"Assess the difficulty of this task:\n"
            f"Task: {task_description}\n\n"
            "Rules:\n"
            "- Assign XP strictly from: 5, 10, 20, 40, 50, 70\n"
            "- Reply with ONLY the number\n"
        )

        response = client.models.generate_content(
            model="gemini-exp-1206", # Using the reliable experimental model
            contents=prompt
        )

        points = int(response.text.strip())
        print(f"✅ AI JUDGEMENT: '{task_description}' = {points} XP")
        return points

    except Exception as e:
        print(f"❌ AI ERROR: {e}")
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

@app.route('/add_task', methods=['POST'])
def add_task():
    task_title = request.form.get('task_name')
    category = request.form.get('category')
    
    # Call AI Function
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


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('dashboard'))
# ----------------------------------------------------

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)