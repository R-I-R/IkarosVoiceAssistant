from __future__ import print_function
import json
from os.path import join, dirname, isfile
from watson_developer_cloud import TextToSpeechV1
import pyaudio
import wave
import sys
import time

text_to_speech = TextToSpeechV1(
    username='464a4abf-53b5-4ff7-a578-1330e295512a',
    password='UygljpTJFaIb',
    x_watson_learning_opt_out=True)  # Optional flag

#print(json.dumps(text_to_speech.voices(), indent=2))
#print(json.dumps(text_to_speech.pronunciation('Watson', pronunciation_format='spr'), indent=2))

def tts(nombre):
	archivo = "audios/"+nombre.replace(" ","")+".wav"
	if isfile(archivo):
		#reproducir(archivo)
		play_audio_file(join(archivo))
	else:
		with open(join(dirname(__file__), archivo),'wb') as audio_file:
			audio_file.write(text_to_speech.synthesize(nombre, accept='audio/wav',voice="es-LA_SofiaVoice"))
			audio_file.close()
		#reproducir(archivo)
		play_audio_file(join(archivo))

def reproducir(file):
	print("reproduciendo")

	ding_wav = wave.open(file, 'rb')
	ding_data = ding_wav.readframes(1024)
	audio = pyaudio.PyAudio()
	stream_out = audio.open(
		format=audio.get_format_from_width(ding_wav.getsampwidth()),
		channels=ding_wav.getnchannels(),
		rate=ding_wav.getframerate(), input=False, output=True)
	stream_out.start_stream()
	stream_out.write(ding_data)
	time.sleep(0.2)
	stream_out.stop_stream()
	stream_out.close()
	audio.terminate()



def play_audio_file(fname):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

tts("Hola Mundo")

