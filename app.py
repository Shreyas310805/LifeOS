import os
import datetime
import time
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Allow HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "LifeOS_Secret_Key_Change_Me"

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifeos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Use your key directly
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "") 
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

# Configure AI immediately
genai.configure(api_key=GOOGLE_API_KEY)

# --- DATABASE MODELS ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default="General")
    xp = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default="Pending")
    due_date = db.Column(db.String(20), nullable=True) 
    due_time = db.Column(db.String(20), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="Shreyas")
    level = db.Column(db.Integer, default=1)
    total_xp = db.Column(db.Integer, default=0)
    is_connected = db.Column(db.Boolean, default=False)
    
    steps = db.Column(db.Integer, default=0)
    calories = db.Column(db.Integer, default=0)
    
    step_history = db.Column(db.Text, default="[]")
    calorie_history = db.Column(db.Text, default="[]")
    
    profile_pic = db.Column(db.String(200), nullable=True)
    health_conditions = db.Column(db.Text, default="") 

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    taken = db.Column(db.Boolean, default=False)

# UPDATED: Removed the "Role" column completely
class SquadMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)

# --- GOOGLE FIT SETUP & AUTH ROUTES ---
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/userinfo.profile' 
]

def get_google_auth_flow():
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://127.0.0.1:5000/callback"]
        }
    }
    return Flow.from_client_config(client_config=client_config, scopes=SCOPES)

@app.route('/login_google')
def login_google():
    flow = get_google_auth_flow()
    flow.redirect_uri = "http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/logout_fit')
def logout_fit():
    user = User.query.first()
    if user:
        user.is_connected = False
        user.steps = 0
        user.calories = 0
        user.step_history = "[]"
        user.calorie_history = "[]"
        db.session.commit()
    return redirect(url_for('fitness'))

@app.route('/callback')
def callback():
    flow = get_google_auth_flow()
    flow.redirect_uri = "http://127.0.0.1:5000/callback"
    try:
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        service = build('fitness', 'v1', credentials=creds)
        
        now = datetime.datetime.now()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_of_today - datetime.timedelta(days=6)
        
        body = {
            "aggregateBy": [
                {"dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"},
                {"dataTypeName": "com.google.calories.expended"}
            ],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(now.timestamp() * 1000)
        }

        daily_data = {}
        for i in range(7):
            d = start_time + datetime.timedelta(days=i)
            day_str = d.strftime('%a')
            daily_data[day_str] = {'steps': 0, 'calories': 0}

        try:
            response = service.users().dataset().aggregate(userId="me", body=body).execute()
            if 'bucket' in response:
                for bucket in response['bucket']: 
                    bucket_time = int(bucket['startTimeMillis'])
                    dt = datetime.datetime.fromtimestamp(bucket_time / 1000.0)
                    day_name = dt.strftime('%a')

                    for dataset in bucket['dataset']:
                        for point in dataset['point']:
                            if point['value']:
                                val = point['value'][0]
                                if 'intVal' in val and day_name in daily_data:
                                    daily_data[day_name]['steps'] += val['intVal']
                                if 'fpVal' in val and day_name in daily_data:
                                    daily_data[day_name]['calories'] += int(val['fpVal'])
                                    
            daily_steps = [{"day": k, "value": v['steps']} for k, v in daily_data.items()]
            daily_calories = [{"day": k, "value": v['calories']} for k, v in daily_data.items()]
            
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")

        user = User.query.first()
        user.is_connected = True
        if len(daily_steps) > 0:
            user.steps = daily_steps[-1]["value"] 
            user.calories = daily_calories[-1]["value"] 
            user.step_history = json.dumps(daily_steps)
            user.calorie_history = json.dumps(daily_calories)
            
        db.session.commit()
        
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return redirect(url_for('fitness'))

    return redirect(url_for('fitness'))

# --- AI HELPER FUNCTION ---
def decide_points_with_ai(task_description):
    try:
        model = genai.GenerativeModel('gemini-flash-latest') 
        prompt = (f"Task: {task_description}\n"
                  "Rules: Difficulty 1-100. Assign XP strictly from: 5, 10, 20, 50, 100. "
                  "Reply ONLY with the raw number. No text.")
        response = model.generate_content(prompt)
        return int(response.text.strip())
    except Exception as e:
        return 10 

# --- PAGE ROUTES ---
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

@app.route('/health')
def health_page():
    user = User.query.first()
    meds = Medication.query.all()
    return render_template('health.html', user=user, meds=meds)

@app.route('/social')
def social():
    user = User.query.first()
    
    # UPDATED: Initialize your specific friends list
    if SquadMember.query.count() == 0:
        Riya = SquadMember(name="Riya", level=5, xp=2450)
        Vaibhav = SquadMember(name="Vaibhav", level=4, xp=2120)
        Prakhar = SquadMember(name="Prakhar", level=4, xp=1890)
        riya = SquadMember(name="Riya", level=3, xp=1500)
        db.session.add_all([Riya, Vaibhav, Prakhar, riya])
        db.session.commit()
        
    squad = SquadMember.query.order_by(SquadMember.xp.desc()).all()
    return render_template('social.html', page='social', user=user, squad=squad)

# --- ACTION ROUTES ---
@app.route('/add_task', methods=['POST'])
def add_task():
    task_title = request.form.get('task_name')
    new_task = Task(
        title=task_title, 
        category=request.form.get('category'), 
        xp=decide_points_with_ai(task_title),
        due_date=request.form.get('due_date'),
        due_time=request.form.get('due_time')
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    user = User.query.first()
    if task and task.status == "Pending":
        task.status = "Done"
        user.total_xp += task.xp
        user.level = 1 + (user.total_xp // 500)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(request.referrer)

# --- MEDICAL ROUTES ---
@app.route('/update_conditions', methods=['POST'])
def update_conditions():
    user = User.query.first()
    user.health_conditions = request.form.get('conditions')
    db.session.commit()
    return redirect('/health')

@app.route('/add_med', methods=['POST'])
def add_med():
    name = request.form.get('med_name')
    time = request.form.get('med_time')
    new_med = Medication(name=name, time=time)
    db.session.add(new_med)
    db.session.commit()
    return redirect('/health')

@app.route('/toggle_med/<int:id>')
def toggle_med(id):
    med = Medication.query.get(id)
    med.taken = not med.taken
    db.session.commit()
    return redirect('/health')

@app.route('/delete_med/<int:id>')
def delete_med(id):
    med = Medication.query.get(id)
    db.session.delete(med)
    db.session.commit()
    return redirect('/health')

# --- SQUAD ROUTES ---
@app.route('/add_squad', methods=['POST'])
def add_squad():
    # UPDATED: No longer asks for or saves a 'role'
    new_member = SquadMember(
        name=request.form.get('name'), 
        level=1,
        xp=0
    )
    db.session.add(new_member)
    db.session.commit()
    return redirect('/social')

@app.route('/delete_squad/<int:id>')
def delete_squad(id):
    member = SquadMember.query.get(id)
    if member:
        db.session.delete(member)
        db.session.commit()
    return redirect('/social')

# --- CHATBOT ROUTE ---
@app.route('/ask_lifey', methods=['POST'])
def ask_lifey():
    user_message = request.json.get('message')
    user = User.query.first()
    tasks = Task.query.all()
    
    task_list = "\n".join([f"- {t.title} ({t.status})" for t in tasks])
    context = f"You are 'Lifey', a strict AI Coach. Conditions: {user.health_conditions}. Tasks: {task_list}. Msg: {user_message}"
    
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(context)
        return jsonify({"reply": response.text})
        
    except Exception as e:
        return jsonify({"reply": "My brain is overheating! Try again in 30 seconds. 🧊"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)