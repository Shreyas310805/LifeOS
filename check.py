import google.generativeai as genai

# 👇 PASTE YOUR KEY HERE
GOOGLE_API_KEY = "AIzaSyAEUJELjrgiafhAEzGjvjeyJMvjylB70w4"

genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 Checking available models for your key...")
try:
    found = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
            found = True
    
    if not found:
        print("❌ No models found. Your API Key might be invalid or the API is not enabled.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")