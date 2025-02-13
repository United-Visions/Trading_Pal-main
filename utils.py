import google.generativeai as genai
import configparser
import json
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

# Configure Gemini
genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=generation_config
)

def get_gemini_response(messages):
    """Centralized function to get responses from Gemini AI"""
    try:
        chat = model.start_chat()
        
        for msg in messages:
            if msg.get("role") == "system":
                chat.send_message(msg["content"])
            else:
                chat.send_message(msg["content"])
        
        return chat.last.text
        
    except Exception as e:
        print(f"[Gemini Error]: {str(e)}")
        return "I encountered an error processing your request."