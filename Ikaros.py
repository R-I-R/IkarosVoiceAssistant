#!/usr/bin/env python
# -*- coding: utf-8 -*-

import speech_recognition as sr
import sys
import signal
import time
import threading

sys.path.insert(1,"snowboy/")
import snowboydecoderIkaros as snowboydecoder
sys.path.insert(1,"tts/")
import tts

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

def reconocervoz(repetir=True):
	r = sr.Recognizer()
	m = sr.Microphone()
	with m as source:
	    tts.tts("Lo escucho")
	    r.adjust_for_ambient_noise(source)
	    #time.sleep(1)
	    audio = r.listen(source)
	try:
	    print("Google Speech Recognition thinks you said: " + r.recognize_google(audio,language="es-CL"))
	except sr.UnknownValueError:
	    tts.tts("Lo siento, no entendí.")
	    if repetir: reconocervoz(False)
	except sr.RequestError as e:
	    print("Could not request results from Google Speech Recognition service; {0}".format(e))




signal.signal(signal.SIGINT, signal_handler)
detector = snowboydecoder.HotwordDetector("snowboy/models/Ikaros.pmdl",sensitivity=0.5)


hiloReconocimientoVoz = threading.Thread(target=detector.start(detected_callback=reconocervoz,interrupt_check=interrupt_callback,sleep_time=0.03),daemon=True)




if not hiloReconocimientoVoz.isAlive():
	detector.terminate()