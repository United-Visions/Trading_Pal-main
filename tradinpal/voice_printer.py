from tradinpal.speech_service import text_to_speech

def print_with_voice(text):
    print(text)
    text_to_speech(text)
