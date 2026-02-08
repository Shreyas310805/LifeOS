from google import genai
import os


GOOGLE_API_KEY = ""

client = genai.Client(api_key=GOOGLE_API_KEY)

print("Checking available models...")
try:
   
    for model in client.models.list():
        print(f"✅ Found: {model.name}")
except Exception as e:
    print(f"❌ Error: {e}")