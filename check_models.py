import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
else:
    try:
        genai.configure(api_key=api_key)
        print(f"✅ API Key found: {api_key[:5]}...")
        print("\n🔍 Fetching available models for you...")
        
        found_any = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Strip 'models/' prefix for easier reading
                model_id = m.name.replace("models/", "")
                print(f" - {model_id}")
                found_any = True
        
        if not found_any:
            print("⚠️ No models found. Your API key might be invalid or has no credits.")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")