import os
import datetime
import json
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
import google.generativeai as genai
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv


from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import User

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "LifeOS_Secret_Key_Change_Me"


cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
genai.configure(api_key=GOOGLE_API_KEY)

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read', 'https://www.googleapis.com/auth/userinfo.profile']


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page' 

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id, db)

def generate_friend_id():
    chars = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choices(chars, k=5))
    return f"FIT-{random_string}"

def update_user(doc_id, data):
    db.collection('users').document(doc_id).update(data)


@app.route('/login')
def login_page():
    
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    id_token = data.get('idToken')
    
    try:
        
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', 'Fitness User')

        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            
            friend_id = generate_friend_id()
            user_ref.set({
                "name": name,
                "email": email,
                "friend_id": friend_id,
                "friends": [], 
                "level": 1,
                "total_xp": 0,
                "is_connected": False,
                "steps": 0,
                "calories": 0,
                "step_history": "[]",
                "calorie_history": "[]",
                "health_conditions": ""
            })

        
        user = User(uid, db)
        login_user(user)
        
        return jsonify({"status": "success", "message": "Logged in successfully"})
        
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))



def get_google_auth_flow():
    client_config = {
        "web": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://127.0.0.1:5000/callback"]}
    }
    return Flow.from_client_config(client_config=client_config, scopes=SCOPES)

def decide_points_with_ai(task_description):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Task: {task_description}\nRules: Difficulty 1-100. Assign XP strictly from: 5, 10, 20, 50, 100. Reply ONLY with the raw number. No text."
        return int(model.generate_content(prompt).text.strip())
    except Exception:
        return 10

@app.route('/login_google')
@login_required
def login_google():
    flow = get_google_auth_flow()
    flow.redirect_uri = "http://127.0.0.1:5000/callback"
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['state'] = state
    return redirect(auth_url)

@app.route('/logout_fit')
@login_required
def logout_fit():
    update_user(current_user.id, {"is_connected": False, "steps": 0, "calories": 0, "step_history": "[]", "calorie_history": "[]"})
    return redirect(url_for('fitness'))

@app.route('/callback')
@login_required
def callback():
    flow = get_google_auth_flow()
    flow.redirect_uri = "http://127.0.0.1:5000/callback"
    try:
        flow.fetch_token(authorization_response=request.url)
        service = build('fitness', 'v1', credentials=flow.credentials)
        now = datetime.datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=6)
        body = {"aggregateBy": [{"dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"}, {"dataTypeName": "com.google.calories.expended"}], "bucketByTime": {"durationMillis": 86400000}, "startTimeMillis": int(start_time.timestamp() * 1000), "endTimeMillis": int(now.timestamp() * 1000)}
        daily_data = {(start_time + datetime.timedelta(days=i)).strftime('%a'): {'steps': 0, 'calories': 0} for i in range(7)}
        
        response = service.users().dataset().aggregate(userId="me", body=body).execute()
        if 'bucket' in response:
            for bucket in response['bucket']:
                day_name = datetime.datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000.0).strftime('%a')
                for dataset in bucket['dataset']:
                    for point in dataset['point']:
                        if point.get('value'):
                            val = point['value'][0]
                            if 'intVal' in val and day_name in daily_data: daily_data[day_name]['steps'] += val['intVal']
                            if 'fpVal' in val and day_name in daily_data: daily_data[day_name]['calories'] += int(val['fpVal'])
        
        daily_steps = [{"day": k, "value": v['steps']} for k, v in daily_data.items()]
        daily_calories = [{"day": k, "value": v['calories']} for k, v in daily_data.items()]
        
        if daily_steps:
            update_user(current_user.id, {"is_connected": True, "steps": daily_steps[-1]["value"], "calories": daily_calories[-1]["value"], "step_history": json.dumps(daily_steps), "calorie_history": json.dumps(daily_calories)})
    except Exception as e:
        print(f"❌ Login Failed: {e}")
    return redirect(url_for('fitness'))


@app.route('/')
@login_required
def dashboard():
    user_data = current_user.to_dict()
    
    tasks = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('tasks').stream()]
    completed = len([t for t in tasks if t.get('status') == "Done"])
    task_percent = int((completed / max(len(tasks), 1)) * 100)
    return render_template('dashboard.html', page='dashboard', user=user_data, tasks=tasks, task_percent=task_percent)

@app.route('/tasks')
@login_required
def tasks():
    return render_template('tasks.html', page='tasks', user=current_user.to_dict(), tasks=[{"id": doc.id, **doc.to_dict()} for doc in db.collection('tasks').stream()])

@app.route('/fitness')
@login_required
def fitness():
    return render_template('fitness.html', page='fitness', user=current_user.to_dict())

@app.route('/health')
@login_required
def health_page():
    return render_template('health.html', user=current_user.to_dict(), meds=[{"id": doc.id, **doc.to_dict()} for doc in db.collection('medications').stream()])

@app.route('/chat')
@login_required
def chat_page():
    
    return render_template('chat.html', page='chat', user=current_user.to_dict())

@app.route('/social')
@login_required
def social():
    user_data = current_user.to_dict()
    friends_list = user_data.get('friends', [])
    
    squad_data = []
   
    for friend_uid in friends_list:
        friend_doc = db.collection('users').document(friend_uid).get()
        if friend_doc.exists:
            friend_dict = friend_doc.to_dict()
            friend_dict['id'] = friend_doc.id
            squad_data.append(friend_dict)
            
    
    squad_data.append(user_data)
            
    squad = sorted(squad_data, key=lambda x: x.get('total_xp', 0), reverse=True)
    return render_template('social.html', page='social', user=user_data, squad=squad)

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    friend_code = request.form.get('friend_code', '').strip().upper()
    
    
    users_ref = db.collection('users').where('friend_id', '==', friend_code).stream()
    
    friend_uid = None
    for doc in users_ref:
        friend_uid = doc.id
        break
        
    
    if friend_uid and friend_uid != current_user.id:
        db.collection('users').document(current_user.id).update({
            "friends": firestore.ArrayUnion([friend_uid])
        })
        
    return redirect('/social')

@app.route('/remove_friend/<friend_id>')
@login_required
def remove_friend(friend_id):
    db.collection('users').document(current_user.id).update({
        "friends": firestore.ArrayRemove([friend_id])
    })
    return redirect('/social')



@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    db.collection('tasks').add({"title": request.form.get('task_name'), "category": request.form.get('category', 'General'), "xp": decide_points_with_ai(request.form.get('task_name')), "status": "Pending", "due_date": request.form.get('due_date'), "due_time": request.form.get('due_time')})
    return redirect(request.referrer)

@app.route('/complete/<task_id>')
@login_required
def complete_task(task_id):
    task_ref = db.collection('tasks').document(task_id)
    task = task_ref.get().to_dict()
    if task and task.get('status') == "Pending":
        task_ref.update({"status": "Done"})
        user_data = current_user.to_dict()
        new_xp = user_data['total_xp'] + task.get('xp', 10)
        update_user(current_user.id, {"total_xp": new_xp, "level": 1 + (new_xp // 500)})
    return redirect(request.referrer)

@app.route('/delete/<task_id>')
@login_required
def delete_task(task_id):
    db.collection('tasks').document(task_id).delete()
    return redirect(request.referrer)

@app.route('/update_conditions', methods=['POST'])
@login_required
def update_conditions():
    update_user(current_user.id, {"health_conditions": request.form.get('conditions')})
    return redirect('/health')

@app.route('/add_med', methods=['POST'])
@login_required
def add_med():
    db.collection('medications').add({"name": request.form.get('med_name'), "time": request.form.get('med_time'), "taken": False})
    return redirect('/health')

@app.route('/toggle_med/<med_id>')
@login_required
def toggle_med(med_id):
    med_ref = db.collection('medications').document(med_id)
    med = med_ref.get().to_dict()
    if med:
        med_ref.update({"taken": not med.get('taken', False)})
    return redirect('/health')

@app.route('/delete_med/<med_id>')
@login_required
def delete_med(med_id):
    db.collection('medications').document(med_id).delete()
    return redirect('/health')

@app.route('/ask_lifey', methods=['POST'])
@login_required
def ask_lifey():
    user_data = current_user.to_dict()
    tasks = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('tasks').stream()]
    task_list = "\n".join([f"- {t.get('title')} ({t.get('status')})" for t in tasks])
    context = f"You are 'Lifey', a strict AI Coach. Conditions: {user_data.get('health_conditions')}. Tasks: {task_list}. Msg: {request.json.get('message')}"
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        return jsonify({"reply": model.generate_content(context).text})
    except Exception:
        return jsonify({"reply": "My brain is overheating! Try again in 30 seconds. 🧊"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)