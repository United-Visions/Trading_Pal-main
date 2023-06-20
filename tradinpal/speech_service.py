import boto3
import wave
import os
import winsound
from config_manager import get_config

session = boto3.Session(
    aws_access_key_id=get_config('AWS_KEYS', 'AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=get_config('AWS_KEYS', 'AWS_SECRET_ACCESS_KEY'),
    region_name=get_config('AWS_KEYS', 'AWS_REGION')
)
polly_client = session.client('polly')

def text_to_speech(text):
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat="pcm",
        VoiceId="Matthew"
    )
    audio = response['AudioStream'].read()
    with wave.open(r"temp.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(audio)
    winsound.PlaySound(r"temp.wav", winsound.SND_FILENAME)
    os.remove(r"temp.wav")
