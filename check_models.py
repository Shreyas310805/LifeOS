import google.generativeai as genai


GOOGLE_API_KEY = ""

genai.configure(api_key=GOOGLE_API_KEY)

print("🔎 SCANNING FOR AVAILABLE MODELS...")
try:
   
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
except Exception as e:
    print(f"❌ ERROR: {e}")