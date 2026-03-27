from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from google.cloud import firestore
from datetime import datetime, timezone
from app.services.gemini_service import gemini_service

bp = Blueprint('ai_chat', __name__)

@bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message: return jsonify({'error': 'No message provided'}), 400
    try:
        db = current_app.config['db']
        user_doc = db.collection('users').document(current_user.id).get().to_dict() or {}
        context = f"You are LifeOS, a health coach. User: {user_doc.get('username', 'User')}. Goals: {user_doc.get('goals', 'Not set')}."
        ai_response = gemini_service.chat(message=user_message, context=context)
        
        if any(word in ai_response.lower() for word in ['recommend', 'suggest', 'try', 'consider']):
            db.collection('ai_insights').add({
                'user_id': current_user.id, 'category': 'general', 'insight_type': 'recommendation',
                'title': 'AI Coach Recommendation', 'description': ai_response[:500],
                'confidence_score': 0.85, 'model_version': current_app.config.get('GEMINI_MODEL', 'gemini-pro'),
                'generated_at': datetime.now(timezone.utc), 'is_read': False
            })
        return jsonify({'response': ai_response, 'model': current_app.config.get('GEMINI_MODEL', 'gemini-pro')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/insights', methods=['GET'])
@login_required
def get_insights():
    db = current_app.config['db']
    insights = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('ai_insights').where('user_id', '==', current_user.id).order_by('generated_at', direction=firestore.Query.DESCENDING).limit(10).stream()]
    return jsonify(insights)

@bp.route('/analyze-health', methods=['POST'])
@login_required
def analyze_health():
    db = current_app.config['db']
    metrics = [{"id": doc.id, **doc.to_dict()} for doc in db.collection('health_metrics').where('user_id', '==', current_user.id).order_by('recorded_at', direction=firestore.Query.DESCENDING).limit(100).stream()]
    if not metrics: return jsonify({'error': 'No health data available'}), 400
    try: 
        user_doc = db.collection('users').document(current_user.id).get().to_dict() or {}
        return jsonify(gemini_service.analyze_health_trends(user_doc, metrics))
    except Exception as e: 
        return jsonify({'error': str(e)}), 500