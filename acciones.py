#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
#paths
sys.path.insert(1,"tts/")

#imports
import json
import apiai
import os
import time
import serial
import tts
import tkinter as tk

#clases

class dialogflow:
	def __init__(self,ClientId,arduino):
		self.ai = apiai.ApiAI(ClientId)
		self.request = self.ai.text_request()
		self.arduino = arduino
		self.silencioAbsolutov = False
		self.controlarVolumen(0,{"number":'30',"valores":''},voz=False)


	def query(self,texto):
		
		self.request.query = texto
		response = self.request.getresponse()

		if os.name == "posix":
			query = json.loads(response.read().decode())["result"]
		else:
			query = json.loads(response.read())["result"]

		intencion = query["metadata"]["intentName"]

		if query["fulfillment"]["speech"] != "":
			#print(query["fulfillment"]["speech"])
			tts.tts(query["fulfillment"]["speech"],self.volumen)

		if intencion == "usar_modulos": self.usar_modulos(query["parameters"])
		elif intencion == "volumen": self.controlarVolumen(0,query["parameters"])
		elif intencion == "bajar_volumen": self.controlarVolumen(-1,query["parameters"])
		elif intencion == "subir_volumen": self.controlarVolumen(1,query["parameters"])
			
		self.request = self.ai.text_request()


	def usar_modulos(self,parametros):
		if parametros["modulos"] == "luz":
			self.arduino.luces(parametros["estados"])
		elif parametros["modulos"] == "cortina":
			self.arduino.cortinas(parametros["estados"],parametros["number"])
		time.sleep(0.1)
		if parametros["modulos1"] != "":
			if parametros["modulos1"] == "luz":
				self.arduino.luces(parametros["estados"])
			elif parametros["modulos1"] == "cortina":
				self.arduino.cortinas(parametros["estados"],parametros["number"])

	def controlarVolumen(self,tipo,parametros,voz=True):
		if self.silencioAbsolutov:
			self.silencioAbsolutov = False
			self.ventilador(True)
			os.system("amixer sset Master {}%".format(self.volumen))

		if tipo < 0:
			if parametros["number"] != '':
				os.system("amixer sset Master {}%-".format(int(parametros["number"])))
				self.volumen -= int(parametros["number"])
			else:
				os.system("amixer sset Master 10%-")
				self.volumen -= 10
		elif tipo > 0:
			if parametros["number"] != '':
				os.system("amixer sset Master {}%+".format(int(parametros["number"])))
				self.volumen += int(parametros["number"])
			else:
				os.system("amixer sset Master 10%+")
				self.volumen += 10
		else:
			if parametros["number"] != '':
				os.system("amixer sset Master {}%".format(int(parametros["number"])))
				self.volumen = int(parametros["number"])
			elif parametros["valores"] != '':
				os.system("amixer sset Master {}%-".format(int(parametros["valores"])))
				self.volumen = int(parametros["valores"])
		if voz: tts.tts("volumen al {}% señor".format(self.volumen),self.volumen)
		self.arduino.setVolumen(self.volumen)

	def silencioAbsoluto(self,commando):
		self.ventilador = commando
		os.system("amixer sset Master 0%")
		self.ventilador(False)
		self.silencioAbsolutov = True


class arduinoCentral:
	envio = 0
	ultimaOrden = ''
	respuestas = 0

	def __init__(self,puerto,vel):
		self.arduino = serial.Serial(puerto, vel,timeout=0.01)
		self.SerialStop = False

	def monitoreo(self):
		envios = 0
		contRespuestas = 0
		reinicio = False
		while True:
			if self.SerialStop: continue
			if self.envio:
				time.sleep(0.15)
				#if self.tiempo+2 > time.time():
				msg = self.arduino.readline().decode()[:-2]
				if msg != '':
					tts.tts(msg,self.volumen)
					if reinicio:
						self.enviarmsg(self.ultimaOrden)
						reinicio = False
						continue
					contRespuestas += 1
					if contRespuestas == 1:
						self.setTimeout(60)
						envios = 0
					if contRespuestas >= self.respuestas:
						self.setTimeout(0.01)
						self.envio = 0
						contRespuestas = 0
						self.respuestas = 0
						continue
				else:
					envios += 1
					self.enviarmsg(self.ultimaOrden)

				if envios >= 3:
					tts.tts("No se ha podido comunicar con el módulo",self.volumen)
					self.setTimeout(0.01)
					envios = 0
					tts.tts("reiniciando",self.volumen)
					self.restart()
					reinicio = True
					

			else:
				msg = self.arduino.readline().decode()[:-2]
				if msg != '':
					print(msg)

			

	def enviarmsg(self,msg):
		self.envio = 1
		self.setTimeout(2.5)
		self.arduino.write(msg.encode())
		self.ultimaOrden = msg
		#self.tiempo = time.time()

	def cortinas(self,estado,number,place="pieza"):
		self.respuestas += 2
		if number != '':
			self.enviarmsg("cortina {} {}".format(place,number))
		else:
			self.enviarmsg("cortina {} {}".format(place,estado))

	def luces(self,estado,place="pieza"):
		self.respuestas += 1
		self.enviarmsg("luz {} {}".format(place,estado))

	def __del__(self):
		self.arduino.close()

	def setTimeout(self,tiempo):
		self.arduino._timeout = tiempo
		self.arduino._reconfigure_port()
		time.sleep(0.1)

	def restart(self):
		import RPi.GPIO as GPIO
		print("reiniciando...")
		self.close()
		time.sleep(0.1)
		GPIO.output(27, True)
		#time.sleep(.01)
		GPIO.output(27, False)
		time.sleep(8)
		self.open()
		time.sleep(0.2)

	def close(self):
		self.SerialStop = True
		self.arduino.close()

	def open(self):
		self.arduino.open()
		self.SerialStop = False

	def setVolumen(self,vol):
		self.volumen = vol

def mapA(x, in_min, in_max, out_min, out_max):
	return (int(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
def mapAround(x, in_min, in_max, out_min, out_max):
	return round((int(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)




class dialogflowTester:
	from tkinter import Tk,Button,Entry,Frame,StringVar,Label
	import speech_recognition as sr

	def __init__(self,ClientId):
		self.ai = apiai.ApiAI(ClientId)
		self.request = self.ai.text_request()


	def queryTest(self,texto):
		self.request.query = texto
		#self.request.timezone = "America/Santiago"
		response = self.request.getresponse()

		if os.name == "posix":
			query = json.loads(response.read().decode())["result"]
		else:
			query = json.loads(response.read())["result"]

		if self.grafico:
			self.parametros.set(query["parameters"])
			self.intencion.set(query["metadata"]["intentName"])
			self.dialogo.set(query["fulfillment"]["speech"])
		else:
			print()
			print("parametros:",query["parameters"])
			print("intencion:",query["metadata"]["intentName"])
			print("dialogo:",query["fulfillment"]["speech"])

		self.request = self.ai.text_request()

	
	def reconocer(self):
		r = self.sr.Recognizer()
		with self.sr.Microphone() as source:
			r.adjust_for_ambient_noise(source)
			if self.grafico:
				self.aviso.set("\t\t\tRecording\t\t\t")
				self.avisos.update_idletasks()
			else: print("Say something!")
			audio = r.listen(source)

		if self.grafico:
			self.aviso.set("\t\t\tFinish\t\t\t")
			self.avisos.update_idletasks()
		else: print("listo")
		
		try:
			texto = r.recognize_google(audio,language="es-CL")
			if self.grafico: self.aviso.set("your say: "+texto)
			else: print("dijiste: " + texto)
			self.queryTest(texto)
		except self.sr.UnknownValueError:
			if self.grafico: self.aviso.set("Google Speech Recognition could not understand audio")
			else:print("Google Speech Recognition could not understand audio")
		except self.sr.RequestError as e:
			if self.grafico: self.aviso.set("Could not request results from Google Speech Recognition service; {0}".format(e))
			else:print("Could not request results from Google Speech Recognition service; {0}".format(e))

	def graficos(self):
		self.grafico = True
		root = self.Tk()
		root.title("dialogflowTester")
		self.aviso = self.StringVar()
		texto = self.StringVar()
		self.parametros = self.StringVar()
		self.intencion = self.StringVar()
		self.dialogo = self.StringVar()
		self.avisos = self.Label(root,textvar=self.aviso,fg="red")
		self.avisos.pack()
		self.Entry(root,textvar=texto,width=100).pack()
		frame = self.Frame(root)
		frame1 = self.Frame(root)
		frame2 = self.Frame(root)
		frame3 = self.Frame(root)
		self.Button(frame,text="Enviar Texto",command= lambda: [self.queryTest(texto.get()),texto.set("")]).pack(side="left")
		self.Button(frame,text="Enviar voz",command=self.reconocer).pack(side="right")
		self.Label(frame1,text="parametros:").pack(side="left")
		self.Label(frame1,textvar=self.parametros).pack(side="right")
		self.Label(frame2,text="intencion:").pack(side="left")
		self.Label(frame2,textvar=self.intencion).pack(side="right")
		self.Label(frame3,text="dialogo:").pack(side="left")
		self.Label(frame3,textvar=self.dialogo).pack(side="right")
		frame.pack()
		frame1.pack()
		frame2.pack()
		frame3.pack()
		root.mainloop()


class bateria:
	import smbus
	
	def __init__(self):
		self.bus = self.smbus.SMBus(1)
		self.direccion = 10
		self.voltaje = None
		self.porcentaje = None

	def monitoreo(self):
		#from threading import Thread
		#Thread(target=self.graficos,daemon=True).start()
		while True:
			data = self.bus.read_i2c_block_data(self.direccion,37,2)
			#print(data)
			voltaje = data[0]*100+data[1]
			self.voltaje.set("V: {}".format(voltaje/100))
			#self.barra.step(mapA(voltaje,300,410,0,100))
			self.porcentaje.set(mapA(voltaje,300,410,0,100))
			time.sleep(1)



#dialogflowTester('9d6dd218d16b457499b933d09b834d5d').graficos()
#aaaa