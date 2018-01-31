from __future__ import print_function
import json
from os.path import join, dirname, isfile
from watson_developer_cloud import TextToSpeechV1
import pyaudio
import wave
import sys
import time
import os

#print(json.dumps(text_to_speech.voices(), indent=2))
#print(json.dumps(text_to_speech.pronunciation('Watson', pronunciation_format='spr'), indent=2))

def tts(nombre):
	archivo = "audios/"+nombre.replace(" ","")+".wav"
	if isfile(archivo):
		reproducir(archivo)
	else:

		text_to_speech = TextToSpeechV1(
    		username='464a4abf-53b5-4ff7-a578-1330e295512a',
    		password='UygljpTJFaIb',
    		x_watson_learning_opt_out=True)  # Optional flag

		with open(join(dirname(__file__), archivo),'wb') as audio_file:
			audio_file.write(text_to_speech.synthesize(nombre, accept='audio/wav',voice="es-LA_SofiaVoice"))
			audio_file.close()
		reproducir(archivo)

def reproducir(file):
	os.system("aplay "+file)


tts("Hola Mundo")

