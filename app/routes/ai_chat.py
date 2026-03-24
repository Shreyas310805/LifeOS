from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import AIInsight
from app.services.gemini_service import gemini_service

bp = Blueprint('ai_chat', __name__)


@bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Chat with Gemini AI health coach"""
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Build user context
        context = f"""
        You are LifeOS, a helpful health and wellness AI coach.

        Current User: {current_user.full_name or current_user.username}
        Goals: {', '.join(current_user.goals) if current_user.goals else 'Not set'}
        Activity Level: {current_user.activity_level or 'Not set'}
        Dietary Preferences: {', '.join(current_user.dietary_preferences) if current_user.dietary_preferences else 'None'}

        Provide encouraging, evidence-based health advice. Be concise but specific.
        If asked about medical conditions, remind them to consult a healthcare professional.
        """

        # Get response from Gemini
        ai_response = gemini_service.chat(
            message=user_message,
            context=context
        )

        # Store as insight if it contains recommendations
        if any(word in ai_response.lower() for word in ['recommend', 'suggest', 'try', 'consider', 'should']):
            try:
                insight = AIInsight(
                    user_id=current_user.id,
                    category='general',
                    insight_type='recommendation',
                    title='AI Coach Recommendation',
                    description=ai_response[:500],
                    confidence_score=0.85,
                    model_version=current_app.config.get('GEMINI_MODEL', 'gemini-pro')
                )
                db.session.add(insight)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to save insight: {e}")

        return jsonify({
            'response': ai_response,
            'model': current_app.config.get('GEMINI_MODEL', 'gemini-pro')
        })

    except ValueError as e:
        # API key not configured
        return jsonify({
            'error': 'AI service not configured',
            'message': str(e),
            'setup_instructions': 'Set GEMINI_API_KEY in your .env file. Get key at https://makersuite.google.com/app/apikey'
        }), 503

    except Exception as e:
        current_app.logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'error': 'Failed to get AI response',
            'message': str(e)
        }), 500


@bp.route('/insights', methods=['GET'])
@login_required
def get_insights():
    """Get AI-generated insights for user"""
    try:
        insights = AIInsight.query.filter_by(user_id=current_user.id) \
            .order_by(AIInsight.generated_at.desc()).limit(10).all()

        return jsonify([{
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'category': i.category,
            'insight_type': i.insight_type,
            'confidence_score': i.confidence_score,
            'is_read': i.is_read,
            'generated_at': i.generated_at.isoformat()
        } for i in insights])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/generate-insight', methods=['POST'])
@login_required
def generate_new_insight():
    """Generate new AI insight on demand"""
    category = request.json.get('category', 'general')

    try:
        insight = gemini_service.generate_insight(current_user, category)
        db.session.add(insight)
        db.session.commit()

        return jsonify({
            'id': insight.id,
            'title': insight.title,
            'description': insight.description,
            'category': insight.category,
            'confidence_score': insight.confidence_score
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analyze-health', methods=['POST'])
@login_required
def analyze_health():
    """Run comprehensive health analysis"""
    from app.models import HealthMetric

    # Get user's recent metrics
    metrics = HealthMetric.query.filter_by(user_id=current_user.id) \
        .order_by(HealthMetric.recorded_at.desc()).limit(100).all()

    if not metrics:
        return jsonify({
            'error': 'No health data available',
            'message': 'Start logging your health metrics to get AI analysis'
        }), 400

    try:
        analysis = gemini_service.analyze_health_trends(current_user, metrics)
        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': str(e)}), 500