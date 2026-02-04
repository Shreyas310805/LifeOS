import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Allow HTTP for local testing (Fixes InsecureTransportError)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "LifeOS_Secret_Key_Change_Me"

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifeos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


GOOGLE_API_KEY = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
# ---------------------------------------------------------

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
    
    # Fitness Data
    is_connected = db.Column(db.Boolean, default=False) # Checks if logged in
    steps = db.Column(db.Integer, default=0)
    calories = db.Column(db.Integer, default=0)
    profile_pic = db.Column(db.String(200), nullable=True) # URL for Google Photo

# --- AI HELPER ---

def decide_points_with_ai(task_description):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # 👇 UPDATED: Using the 'latest' alias which has better limits
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = (f"Task: {task_description}\n"
                  "Rules: Difficulty 1-100. Assign XP strictly from: 5, 10, 20, 50, 100. "
                  "Reply ONLY with the raw number. No text.")
        
        response = model.generate_content(prompt)
        return int(response.text.strip())

    except Exception as e:
        # If it fails, print the error but don't crash the app
        print(f"❌ AI Error: {e}")
        return 10

# --- GOOGLE FIT OAUTH SETUP ---

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
    user.is_connected = False
    user.steps = 0
    user.calories = 0
    user.profile_pic = None
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/callback')
def callback():
    flow = get_google_auth_flow()
    flow.redirect_uri = "http://127.0.0.1:5000/callback"
    
    try:
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        # 1. Fetch Profile Picture
        session_request = flow.authorized_session()
        profile_info = session_request.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        profile_pic = profile_info.get('picture', '')

        # 2. Fetch Fitness Data
        service = build('fitness', 'v1', credentials=creds)
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(days=1)
        
        body = {
            "aggregateBy": [
                {"dataTypeName": "com.google.step_count.delta"},
                {"dataTypeName": "com.google.calories.expended"}
            ],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(now.timestamp() * 1000)
        }

        steps = 0
        calories = 0
        
        try:
            response = service.users().dataset().aggregate(userId="me", body=body).execute()
            if 'bucket' in response:
                bucket = response['bucket'][0]
                for dataset in bucket['dataset']:
                    for point in dataset['point']:
                        if point['value']:
                            val = point['value'][0]
                            if 'intVal' in val: steps += val['intVal']
                            if 'fpVal' in val: calories += int(val['fpVal'])
        except Exception as e:
            print(f"Error fetching stats: {e}")

        # 3. SAVE TO DATABASE (Crucial Step)
        user = User.query.first()
        user.is_connected = True  # <--- FORCE THIS TO TRUE
        user.steps = steps
        user.calories = calories
        user.profile_pic = profile_pic
        db.session.commit()
        
    except Exception as e:
        print(f"Login Failed: {e}")
        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)