import os
import google.generativeai as genai
from typing import Dict, List, Optional
from flask import current_app

class GeminiService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self):
        if self._initialized: return
        api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key: raise ValueError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=current_app.config.get('GEMINI_MODEL', 'gemini-pro'),
            generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 40, "max_output_tokens": 2048},
            safety_settings=[{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}]
        )
        self._initialized = True

    @property
    def model(self):
        if not self._initialized: self._initialize()
        return self._model

    def chat(self, message: str, context: str = "", chat_history: List[Dict] = None) -> str:
        chat = self.model.start_chat(history=chat_history or [])
        return chat.send_message(f"{context}\n\nUser: {message}" if context else message).text

    def analyze_health_trends(self, user_dict, metrics_list) -> Dict:
        metrics_summary = "\n".join([f"- {m.get('metric_type')}: {m.get('value')} {m.get('unit')} ({m.get('recorded_at')})" for m in metrics_list[-30:]]) if metrics_list else "No recent metrics available."
        prompt = f"Analyze health data for {user_dict.get('username', 'user')}.\nMetrics:\n{metrics_summary}\nProvide JSON: {{\"trends\": [], \"concerns\": [], \"recommendations\": [], \"health_score\": 85, \"summary\": \"\"}}"
        
        import json, re
        try:
            text = self.model.generate_content(prompt).text
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            return json.loads(json_match.group(1) if json_match else text)
        except Exception:
            return {"trends": [], "concerns": ["Error"], "recommendations": ["Try again"], "health_score": None, "summary": "Unavailable"}

gemini_service = GeminiService()