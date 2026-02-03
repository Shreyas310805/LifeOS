import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("AIzaSyB2T2Fz-uMnwnSuy2_mA1p286PAPJcJRPw"))
model = genai.GenerativeModel("gemini-pro")

def get_ai_suggestion(progress: int):
    prompt = f"""
    User has completed {progress}% of their daily goals.
    Provide a professional productivity suggestion in one sentence.
    """
    return model.generate_content(prompt).text

def generate_quiz(task_title: str):
    prompt = f"Create 2 simple questions to verify completion of: {task_title}"
    return model.generate_content(prompt).text
def classify_task(task_title: str):
    prompt = f"""
    You are a productivity assistant.
    Classify the difficulty of this task as one of:
    easy, medium, or hard.

    Task: "{task_title}"

    Respond ONLY with one word: easy, medium, or hard.
    """

    response = model.generate_content(prompt)
    return response.text.strip().lower()
