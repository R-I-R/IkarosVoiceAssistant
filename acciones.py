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
			tts.tts(query["fulfillment"]["speech"])

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
			os.system("amixer sset Master {}%".format(mapAround(self.volumen,0,100,34,100)))

		if tipo < 0:
			if parametros["number"] != '':
				number = mapAround(parametros["number"],0,100,34,100)
				os.system("amixer sset Master {}%-".format(number))
				self.volumen -= int(parametros["number"])
			else:
				os.system("amixer sset Master 7%-")
				self.volumen -= 10
		if tipo > 0:
			if parametros["number"] != '':
				number = mapAround(parametros["number"],0,100,34,100)
				os.system("amixer sset Master {}%+".format(number))
				self.volumen += int(parametros["number"])
			else:
				os.system("amixer sset Master 7%+")
				self.volumen += 10
		else:
			if parametros["number"] != '':
				number = mapAround(parametros["number"],0,100,34,100)
				os.system("amixer sset Master {}%".format(number))
				self.volumen = int(parametros["number"])
			elif parametros["valores"] != '':
				valores = mapAround(parametros["valores"],0,100,34,100)
				os.system("amixer sset Master {}%-".format(valores))
				self.volumen = int(parametros["valores"])
		if voz: tts.tts("volumen al {}% señor".format(self.volumen))

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
		self.arduino = serial.Serial(puerto, vel,timeout=0)
		self.reinicio = False

	def monitoreo(self):
		envios = 0
		contRespuestas = 0
		while True:
			if self.reinicio: continue
			if self.envio:
				time.sleep(0.15)
				#if self.tiempo+2 > time.time():
				msg = self.arduino.readline().decode()[:-2]
				if msg != '':
					tts.tts(msg)
					contRespuestas += 1
					if contRespuestas == 1:
						self.setTimeout(60)
						envios = 0
					if contRespuestas >= self.respuestas:
						self.setTimeout(0)
						self.envio = 0
						contRespuestas = 0
						self.respuestas = 0
						continue
				else:
					envios += 1
					self.enviarmsg(self.ultimaOrden)

				if envios >= 4:
					tts.tts("No se ha podido comunicar con el módulo")
					self.setTimeout(0)
					envios = 0
					self.envio = 0
					self.restart()
					print("serial reiniciado")

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
		print("reiniciando...")
		self.reinicio = True
		self.arduino.close()
		time.sleep(0.1)
		self.arduino.open()
		self.reinicio = False

def mapA(x, in_min, in_max, out_min, out_max):
	return (int(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
def mapAround(x, in_min, in_max, out_min, out_max):
	return round((int(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)



#arduino = arduinoCentral("","")
#print("creando dialogflow")
#IkarosApiAI = dialogflow('9d6dd218d16b457499b933d09b834d5d',arduino)
#print("enviando query")
#IkarosApiAI.query("abre las cortinas y prende las luces")
#time.sleep(5)
#print("enviando query2")
#IkarosApiAI.query("desactiva las luces y abre las cortinas al 95%")