import os
import google.generativeai as genai
from typing import Dict, List, Optional
from flask import current_app
from app.models import HealthMetric, AIInsight


class GeminiService:
    """Google Gemini 3 AI Service for LifeOS"""

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern to ensure single configuration"""
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self):
        """Lazy initialization of Gemini"""
        if self._initialized:
            return

        api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')

        if not api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY in your .env file. "
                "Get your key at: https://makersuite.google.com/app/apikey"
            )

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Set up the model
        model_name = current_app.config.get('GEMINI_MODEL', 'gemini-pro')

        # Generation config
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Safety settings (adjust as needed for health content)
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"  # Allow some medical discussion
            }
        ]

        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        self._initialized = True

    @property
    def model(self):
        """Get or initialize model"""
        if not self._initialized:
            self._initialize()
        return self._model

    def chat(self, message: str, context: str = "", chat_history: List[Dict] = None) -> str:
        """Send message to Gemini and get response"""
        try:
            # Start chat session
            chat = self.model.start_chat(history=chat_history or [])

            # Prepare full prompt with context
            full_prompt = f"{context}\n\nUser: {message}" if context else message

            response = chat.send_message(full_prompt)

            return response.text

        except Exception as e:
            current_app.logger.error(f"Gemini API error: {str(e)}")
            raise

    def analyze_health_trends(self, user, metrics: List[HealthMetric]) -> Dict:
        """Analyze health metrics using Gemini"""

        # Format metrics for AI
        metrics_summary = self._format_metrics(metrics)

        prompt = f"""
        You are a health analytics AI. Analyze the following health data for {user.full_name or 'the user'}.

        User Profile:
        - Age: {self._get_age(user.date_of_birth) or 'Unknown'}
        - Activity Level: {user.activity_level or 'Not specified'}
        - Goals: {', '.join(user.goals) if user.goals else 'None specified'}

        Recent Health Metrics (last 30 days):
        {metrics_summary}

        Provide a JSON response with this structure:
        {{
            "trends": ["trend 1", "trend 2"],
            "concerns": ["concern 1" or null],
            "recommendations": ["action 1", "action 2"],
            "health_score": 85,
            "summary": "brief overall assessment"
        }}

        Be specific, actionable, and encouraging. Focus on patterns and correlations.
        """

        try:
            response = self.model.generate_content(prompt)

            # Parse JSON from response
            import json
            import re

            # Extract JSON from markdown code blocks if present
            text = response.text
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)

            return json.loads(text)

        except Exception as e:
            current_app.logger.error(f"Health analysis error: {str(e)}")
            return {
                "trends": [],
                "concerns": ["Unable to analyze data"],
                "recommendations": ["Please try again later"],
                "health_score": None,
                "summary": "Analysis temporarily unavailable"
            }

    def generate_personalized_plan(self, user, goal: str, plan_type: str = "fitness") -> str:
        """Generate personalized fitness or nutrition plan"""

        prompt = f"""
        Create a detailed, personalized {plan_type} plan for achieving: {goal}

        User Profile:
        - Name: {user.full_name or 'User'}
        - Age: {self._get_age(user.date_of_birth) or 'Unknown'}
        - Current Weight: {user.weight_kg}kg
        - Height: {user.height_cm}cm
        - Activity Level: {user.activity_level or 'Not specified'}
        - Goals: {', '.join(user.goals) if user.goals else 'General wellness'}
        - Dietary Preferences: {', '.join(user.dietary_preferences) if user.dietary_preferences else 'None'}

        Requirements:
        1. Provide specific, actionable daily/weekly schedule
        2. Include measurable milestones
        3. Account for rest and recovery
        4. Suggest adjustments based on progress
        5. Keep safety as top priority

        Format the response in clear sections with bullet points.
        """

        response = self.model.generate_content(prompt)
        return response.text

    def get_nutrition_advice(self, meal_description: str, user_goals: List[str] = None) -> Dict:
        """Analyze meal and provide nutritional advice"""

        prompt = f"""
        Analyze this meal: "{meal_description}"

        User Goals: {', '.join(user_goals) if user_goals else 'General health'}

        Provide:
        1. Estimated nutritional breakdown (calories, protein, carbs, fat, fiber)
        2. Health assessment (good/bad/moderate)
        3. Suggestions for improvement
        4. How it aligns with user's goals

        Return as JSON:
        {{
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "assessment": "description",
            "suggestions": ["suggestion 1"],
            "goal_alignment": "description"
        }}
        """

        response = self.model.generate_content(prompt)

        import json
        import re
        text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        return json.loads(text)

    def generate_insight(self, user, category: str = "general") -> AIInsight:
        """Generate AI insight for user"""

        # Get recent context
        from app.models import HealthMetric, Task, Fitness

        recent_metrics = HealthMetric.query.filter_by(user_id=user.id) \
            .order_by(HealthMetric.recorded_at.desc()).limit(10).all()

        pending_tasks = Task.query.filter_by(user_id=user.id, status='pending').count()
        recent_workouts = Fitness.query.filter_by(user_id=user.id) \
            .order_by(Fitness.performed_at.desc()).limit(5).all()

        context = f"""
        User has {pending_tasks} pending tasks.
        Recent activity: {len(recent_workouts)} workouts logged.
        Health metrics: {len(recent_metrics)} recent entries.
        """

        prompt = f"""
        Generate a personalized {category} insight for a health app user.

        User Context: {context}
        User Goals: {', '.join(user.goals) if user.goals else 'General wellness'}

        Create an encouraging, specific insight that:
        1. Acknowledges their recent activity
        2. Provides one actionable recommendation
        3. Has a confidence score (0.0-1.0)

        Return JSON:
        {{
            "title": "Short title",
            "description": "Detailed insight text (max 500 chars)",
            "confidence_score": 0.85,
            "category": "{category}"
        }}
        """

        response = self.model.generate_content(prompt)

        import json
        import re
        text = response.text
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        data = json.loads(text)

        insight = AIInsight(
            user_id=user.id,
            category=data.get('category', category),
            insight_type='recommendation',
            title=data.get('title', 'AI Insight'),
            description=data.get('description', ''),
            confidence_score=data.get('confidence_score', 0.8),
            model_version=current_app.config.get('GEMINI_MODEL', 'gemini-pro')
        )

        return insight

    def _format_metrics(self, metrics: List[HealthMetric]) -> str:
        """Format metrics for AI prompt"""
        if not metrics:
            return "No recent metrics available."

        lines = []
        for m in metrics[-30:]:  # Last 30 entries
            lines.append(f"- {m.metric_type}: {m.value} {m.unit} ({m.recorded_at.strftime('%Y-%m-%d')})")

        return "\n".join(lines)

    def _get_age(self, birth_date) -> Optional[int]:
        """Calculate age from birth date"""
        if not birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# Singleton instance
gemini_service = GeminiService()