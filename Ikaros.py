#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
#paths
sys.path.insert(1,"./snowboy/")
sys.path.insert(1,"tts/")

#imports
import RPi.GPIO as GPIO
import speech_recognition as sr
import signal
import time
import threading
from acciones import *
from tkinter import ttk
import tkinter as tk
import snowboydecoderIkaros as snowboydecoder
import tts

interrupted = False
dia = True
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.output(17, True)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

def reconocervoz(repetir=True):
	tts.tts("Lo escucho",IkarosApiAI.volumen)
	#time.sleep(1)

	r = sr.Recognizer()
	m = sr.Microphone()

	with m as source:
	    r.adjust_for_ambient_noise(source)
	    audio = r.listen(source)
	try:
		texto = r.recognize_google(audio,language="es-CL")
		print("Google Speech Recognition thinks you said: "+texto)
		if texto == "Buenos días":buenosDias()
		elif texto == "buenas noches":buenasNoches()
		elif texto == "silencio absoluto": IkarosApiAI.silencioAbsoluto(ventilador)
		else: IkarosApiAI.query(texto)
	except sr.UnknownValueError:
	    tts.tts("Lo siento, no entendí.",IkarosApiAI.volumen)
	    if repetir: reconocervoz(False)
	except sr.RequestError:
	    tts.tts("no hay respuesta de Google",IkarosApiAI.volumen)

def ventilador(estado):
	GPIO.output(17, estado)

def buenosDias():
	global hiloTemporal
	dia = True
	ventilador(True)
	IkarosApiAI.controlarVolumen(0,{"number":'60',"valores":''},voz=False)
	tts.tts("buenos díasseñor",IkarosApiAI.volumen)
	IkarosApiAI.query("prende la luz y abre la cortina")
	try: hiloTemporal.cancel()
	except: pass

def buenasNoches():
	global hiloTemporal
	dia = False
	ventilador(False)
	IkarosApiAI.controlarVolumen(0,{"number":'30',"valores":''},voz=False)
	tts.tts("buenas noches señor",IkarosApiAI.volumen)
	IkarosApiAI.query("apaga la luz y cierra la cortina")
	hiloTemporal = threading.Timer(7200, ventilador,args=(True,))
	hiloTemporal.start()

Arduino = arduinoCentral("/dev/ttyUSB0",9600)
Bateria = bateria()
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
	BrevivirReconocimientoVoz.config(state="disabled")


#declaracion de hilos
pararReconocimientoVoz = threading.Event()

hiloTemporal = None
hiloReconocimientoVoz = threading.Thread(target=iniciarReconocimientoVoz,args=(pararReconocimientoVoz,),daemon=True)
hiloMonitoreoArduino = threading.Thread(target=Arduino.monitoreo,daemon=True)
hiloMonitoreoBateria = threading.Thread(target=Bateria.monitoreo,daemon=True)

#marcos tkinter
root = tk.Tk()
controlF = tk.Frame(root)
bateriaF = tk.Frame(root)

#variables tkinter
Bateria.voltaje = tk.StringVar()
Bateria.porcentaje = tk.IntVar()

#objetos tkinter
tk.Button(controlF,text="Parar reconocimiento de voz",command=pararReconocimientoVoz.set).pack()
BrevivirReconocimientoVoz = tk.Button(controlF,text="Iniciar reconocimiento de voz",command=revivirReconocimientoVoz,state="disabled")
BrevivirReconocimientoVoz.pack()
tk.Button(controlF,text="Reiniciar comunicacion Serial",command=Arduino.restart).pack()
tk.Button(controlF,text="Parar comunicacion Serial",command=Arduino.close).pack()
tk.Button(controlF,text="Iniciar comunicacion Serial",command=Arduino.open).pack()
controlF.pack(side="left")

ttk.Progressbar(bateriaF,variable=Bateria.porcentaje,length=200).pack()
tk.Label(bateriaF,textvar=Bateria.voltaje).pack()
bateriaF.pack(side="left")


#inicio de hilos
hiloReconocimientoVoz.start()
hiloMonitoreoArduino.start()
hiloMonitoreoBateria.start()

#inicio de loop
root.mainloop()

#GPIO.cleanup()
