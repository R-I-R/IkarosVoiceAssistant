#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,json,apiai,os

sys.path.insert(1,"tts/")
import tts

class dialogflow:
	def apiaiquery(texto):
		ai = apiai.ApiAI('9d6dd218d16b457499b933d09b834d5d')
		request = ai.text_request()
		request.lang = 'es'  # optional, default value equal 'en'
		request.session_id = "ikarosid"
		request.query = texto

		response = request.getresponse()
		if os.name == "posix":
			query = json.loads(response.read().decode())["result"]
		else:
			query = json.loads(response.read())["result"]

		print("{}--------{}".format(query["metadata"]["intentName"],query["parameters"]))

		if query["fulfillment"]["speech"] != "":
			print(query["fulfillment"]["speech"])
			#tts.tts(query["result"]["fulfillment"]["speech"])

		if query["metadata"]["intentName"] == "usar_modulos":
			usar_modulos(query["parameters"])
			

	def usar_modulos(parametros):
		if parametros["modulos"] == "luz":
			if parametros["estados"] == "on":
				print("prender luces pieza")
			else: print("apagar luces pieza")
		elif parametros["modulos"] == "cortina":
			if parametros["number"] == '':
				if parametros["estados"] == "on":
					print("abrir cortinas pieza")
				else: print("cerrar cortinas pieza")
			else: print("cortinas pieza al "+parametros["number"])
		
		if parametros["modulos1"] != "":
			if parametros["modulos1"] == "luz":
				if parametros["estados1"] == "on":
					print("prender luces pieza")
				else: print("apagar luces pieza")
			elif parametros["modulos1"] == "cortina":
				if parametros["number"] == '':
					if parametros["estados1"] == "on":
						print("abrir cortinas pieza")
					else: print("cerrar cortinas pieza")
				else: print("cortinas pieza al "+parametros["number"])



#apiaiquery("abre las cortinas al 60% y apaga las luces")