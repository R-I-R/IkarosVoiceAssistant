#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import speech_recognition as sr
import sys
import signal
import time
import threading
from acciones import *
from tkinter import *

sys.path.insert(1,"snowboy/")
import snowboydecoderIkaros as snowboydecoder
sys.path.insert(1,"tts/")
import tts

interrupted = False
dia = True
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

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
		texto = r.recognize_google(audio,language="es-CL")
		print("Google Speech Recognition thinks you said: "+texto)
		if texto == "Buenos días":buenosDias()
		elif texto == "buenas noches":buenasNoches()
		else: IkarosApiAI.query(texto)
	except sr.UnknownValueError:
	    tts.tts("Lo siento, no entendí.")
	    if repetir: reconocervoz(False)
	except sr.RequestError as e:
	    tts.tts("no hay respuesta de Google")


def buenosDias():
	global hiloTemporal
	dia = True
	GPIO.output(17, True)
	tts.tts("buenos díasseñor")
	IkarosApiAI.query("prende la luz y abre la cortina")
	try:
		hiloTemporal.cancel()
	except:
		pass
def buenasNoches():
	global hiloTemporal
	dia = False
	GPIO.output(17, False)
	tts.tts("buenas noches señor")
	IkarosApiAI.query("apaga la luz y cierra la cortina")
	hiloTemporal = threading.Timer(7200, GPIO.output,args=(17,True))
	hiloTemporal.start()

Arduino = arduinoCentral("/dev/ttyACM0",9600)
IkarosApiAI = dialogflow('9d6dd218d16b457499b933d09b834d5d',Arduino)


signal.signal(signal.SIGINT, signal_handler)
def iniciarReconocimientoVoz(evento):
	global BrevivirReconocimientoVoz
	evento.clear()
	detector = snowboydecoder.HotwordDetector("snowboy/models/Ikaros.pmdl",sensitivity=0.35)
	detector.start(detected_callback=reconocervoz,interrupt_check=interrupt_callback,sleep_time=0.03,evento=evento)
	detector.terminate()
	BrevivirReconocimientoVoz.config(state="normal")

def revivirReconocimientoVoz():
	global hiloReconocimientoVoz,pararReconocimientoVoz
	pararReconocimientoVoz.clear()
	hiloReconocimientoVoz = threading.Thread(target=iniciarReconocimientoVoz,args=(pararReconocimientoVoz,),daemon=True)
	hiloReconocimientoVoz.start()


pararReconocimientoVoz = threading.Event()

hiloTemporal = None
hiloReconocimientoVoz = threading.Thread(target=iniciarReconocimientoVoz,args=(pararReconocimientoVoz,),daemon=True)
hiloMonitoreoArduino = threading.Thread(target=Arduino.monitoreo,daemon=True)

hiloReconocimientoVoz.start()
hiloMonitoreoArduino.start()

root = Tk()
Button(root,text="parar reconocimiento de voz",command=pararReconocimientoVoz.set).pack()
BrevivirReconocimientoVoz = Button(root,text="iniciar reconocimiento de voz",command=revivirReconocimientoVoz,state="disabled")
BrevivirReconocimientoVoz.pack()
root.mainloop()

#GPIO.cleanup()