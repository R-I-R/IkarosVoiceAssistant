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
			if parametros["estados"] == "on":
				self.arduino.enviarmsg("prender luces pieza")
			else: self.arduino.enviarmsg("apagar luces pieza")
		elif parametros["modulos"] == "cortina":
			if parametros["number"] == '':
				if parametros["estados"] == "on":
					self.arduino.enviarmsg("abrir cortinas pieza")
				else: self.arduino.enviarmsg("cerrar cortinas pieza")
			else: self.arduino.enviarmsg("cortinas pieza al "+parametros["number"])
		
		if parametros["modulos1"] != "":
			if parametros["modulos1"] == "luz":
				if parametros["estados1"] == "on":
					self.arduino.enviarmsg("prender luces pieza")
				else: self.arduino.enviarmsg("apagar luces pieza")
			elif parametros["modulos1"] == "cortina":
				if parametros["number"] == '':
					if parametros["estados1"] == "on":
						self.arduino.enviarmsg("abrir cortinas pieza")
					else: self.arduino.enviarmsg("cerrar cortinas pieza")
				else: self.arduino.enviarmsg("cortinas pieza al "+parametros["number"])


class arduinoCentral:
	envio = 0
	def __init__(self,puerto,vel):
		self.arduino = serial.Serial(puerto, vel)

	def monitoreo(self):
		while True:
			if self.envio > 1:
				msg = self.arduino.readline().decode()[:-2]
				tts.tts(msg)

			else:
				msg = self.arduino.readline().decode()[:-2]
				print(msg)

	def enviarmsg(self,msg):
		self.envio = 1
		self.arduino.write(msg.encode())
		self.envio = 2

	def __del__(self):
		self.arduino.close()




#print("creando dialogflow")
#IkarosApiAI = dialogflow(ClientId='9d6dd218d16b457499b933d09b834d5d')
#print("enviando query")
#IkarosApiAI.query("abre las cortinas al 60% y apaga las luces")
#time.sleep(5)
#print("enviando query2")
#IkarosApiAI.query("desactiva las luces y abre las cortinas al 95%")