#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,json,apiai,os,time,serial

sys.path.insert(1,"tts/")
import tts

class dialogflow:
	def __init__(self,ClientId,arduino):
		self.ai = apiai.ApiAI(ClientId)
		self.request = self.ai.text_request()
		self.arduino = arduino
		

	def query(self,texto):
		
		self.request.query = texto
		response = self.request.getresponse()

		if os.name == "posix":
			query = json.loads(response.read().decode())["result"]
		else:
			query = json.loads(response.read())["result"]

		print("{}--------{}".format(query["metadata"]["intentName"],query["parameters"]))

		if query["fulfillment"]["speech"] != "":
			#print(query["fulfillment"]["speech"])
			tts.tts(query["fulfillment"]["speech"])

		if query["metadata"]["intentName"] == "usar_modulos":
			self.usar_modulos(query["parameters"])
			
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


class arduinoCentral:
	envio = 0
	ultimaOrden = ''
	respuestas = 1

	def __init__(self,puerto,vel):
		self.arduino = serial.Serial(puerto, vel,timeout=2.5)

	def monitoreo(self):
		envios = 0
		contRespuestas = 0
		while True:
			if self.envio:
				#if self.tiempo+2 > time.time():
				msg = self.arduino.readline().decode()[:-2]
				if msg != '':
					tts.tts(msg)
					contRespuestas += 1
					if contRespuestas >= self.respuestas:
						self.envio = 0
						contRespuestas = 0
				else:
					envios += 1
					self.enviarmsg(self.ultimaOrden)

			else:
				msg = self.arduino.readline().decode()[:-2]
				if msg != '':
					print(msg)

			if envios >= 3:
				tts.tts("No se ha podido comunicar con el módulo")
				envios = 0
				self.envio = 0

	def enviarmsg(self,msg):
		self.envio = 1
		time.sleep(0.1)
		self.arduino.write(msg.encode())
		self.ultimaOrden = msg
		#self.tiempo = time.time()

	def cortinas(self,estado,number,place="pieza"):
		self.respuestas = 2
		if number != '':
			self.enviarmsg("cortina {} {}".format(place,number))
		else:
			self.enviarmsg("cortina {} {}".format(place,estado))

	def luces(self,estado,place="pieza"):
		self.respuestas = 1
		self.enviarmsg("luz {} {}".format(place,estado))

	def __del__(self):
		self.arduino.close()



#arduino = arduinoCentral("","")
#print("creando dialogflow")
#IkarosApiAI = dialogflow('9d6dd218d16b457499b933d09b834d5d',arduino)
#print("enviando query")
#IkarosApiAI.query("abre las cortinas y prende las luces")
#time.sleep(5)
#print("enviando query2")
#IkarosApiAI.query("desactiva las luces y abre las cortinas al 95%")