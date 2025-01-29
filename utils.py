import google.generativeai as genai
import configparser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

# Singleton instance for Gemini model
_gemini_model = None

def get_gemini_model():
    """Get or create Gemini model instance"""
    global _gemini_model
    if not _gemini_model:
        try:
            genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            _gemini_model = genai.GenerativeModel(model_name="gemini-pro", 
                                                generation_config=generation_config)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    return _gemini_model

def get_gemini_response(messages):
    """Get response from Gemini model"""
    try:
        model = get_gemini_model()
        chat = model.start_chat(history=[])
        
        for msg in messages:
            content = msg.get("content", "")
            chat.send_message(content)
            
        return chat.last.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Sorry, I encountered an error processing your request."
