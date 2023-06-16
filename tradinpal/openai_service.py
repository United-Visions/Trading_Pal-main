import openai
from tradinpal.config_manager import get_config

openai.api_key = get_config('API_KEYS', 'OPENAI_API_KEY')
MAX_TOKENS = 16000

def create_chat_completion(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']
