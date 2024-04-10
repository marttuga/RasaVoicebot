import os
import requests
import re
import spacy
from gtts import gTTS
import playsound
import azure.cognitiveservices.speech as speechsdk
import time

os.environ["SPEECH_KEY"] = "b9bff20fbfd84b42b8a3865d3c5640e3"
os.environ["SPEECH_REGION"] = "westeurope"

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get("SPEECH_KEY"), region=os.environ.get("SPEECH_REGION"))
speech_config.speech_recognition_language = "en-US"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

nlp = spacy.load("en_core_web_sm")
bot_message = ""
message = ""

r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": "Hello"})

print("Bot says:", end=' ')

for i in r.json():
    bot_message = i['text']
    print(f"{bot_message}")

while bot_message != "Bye" and bot_message != 'thanks':
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once()
    message = speech_recognition_result.text
    print("Speech recognition result:", message)

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    message = re.sub(email_pattern, "email", message)

    doc = nlp(message)
    converted_message = ""
    for token in doc:
        if token.ent_type_ == "CARDINAL":
            converted_message += str(token.text) + " "
        else:
            converted_message += token.text + " "
    message = converted_message.strip()

    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})
    time.sleep(2)

    print("Bot says:", end=' ')
    for i in r.json():
        bot_message = i['text']
        print(f"{bot_message}")

    myobj = gTTS(text=bot_message)
    myobj.save("welcome.mp3")
    print('Saved')

    playsound.playsound("welcome.mp3") 
    os.remove('welcome.mp3')
#pip install playsound==1.2.2