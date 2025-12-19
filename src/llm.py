import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found in .env file")

genai.configure(api_key=API_KEY)

class GeminiClient:
    def __init__(self, model_name='gemini-2.5-flash'):
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    def generate_decision(self, system_prompt, user_context, retries=3):
        for i in range(retries):
            try:
                response = self.model.generate_content(
                    contents=[{"role": "user", "parts": [f"{system_prompt}\n\n{user_context}"]}]
                )
                return json.loads(response.text)
            except Exception as e:
                print(f"⚠️ API Error (Attempt {i+1}): {e}")
                time.sleep(2)  # Backoff
        return None