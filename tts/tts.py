from __future__ import print_function
import json
from os.path import join, dirname, isfile
import sys
import os

#print(json.dumps(text_to_speech.voices(), indent=2))
#print(json.dumps(text_to_speech.pronunciation('Watson', pronunciation_format='spr'), indent=2))
equipo = os.name

def tts(nombre):

	#archivo = ""
	#for a in nombre:
	#	if a.isalnum():
	#		archivo += a
	#	else:
	#		if a == "?": archivo += "-"

	archivo = nombre.replace(" ","").replace("?","-").replace(":","").replace("|","").replace("<","").replace(">","").replace("\\","").replace("/","").replace("*","").replace('"',"")

	if equipo == "posix": archivo = os.getcwd()+"/tts/audios/"+archivo+".wav"
	else : archivo = "audios/"+archivo+".wav"
	if isfile(archivo):
		reproducir(archivo)
	else:

		from watson_developer_cloud import TextToSpeechV1

		text_to_speech = TextToSpeechV1(
    		username='464a4abf-53b5-4ff7-a578-1330e295512a',
    		password='UygljpTJFaIb',
    		x_watson_learning_opt_out=True)  # Optional flag

		with open(join(dirname(__file__), archivo),'wb') as audio_file:
			audio_file.write(text_to_speech.synthesize(nombre, accept='audio/wav',voice="es-ES_EnriqueVoice"))
			audio_file.close()
		reproducir(archivo)

def reproducir(file):
	if equipo == "posix":
		os.system("aplay "+file)
	else:
		if isfile((os.getcwd()+"\\"+file).replace("/","\\")):
			os.system("start wmplayer "+(os.getcwd()+"\\"+file).replace("/","\\"))
		else: os.system("start wmplayer "+(os.getcwd()+"\\tts\\"+file).replace("/","\\"))

