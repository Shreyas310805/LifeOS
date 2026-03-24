import google.generativeai as genai

# Paste your key directly here for a quick check
GOOGLE_API_KEY = ""

genai.configure(api_key=GOOGLE_API_KEY)

print("🔎 SCANNING FOR AVAILABLE MODELS...")
try:
    # This will list all models your key can access
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
except Exception as e:
    print(f"❌ ERROR: {e}")