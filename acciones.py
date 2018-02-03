#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,json,apiai

sys.path.insert(1,"tts/")
import tts

def apiaiquery(texto):
    ai = apiai.ApiAI('9d6dd218d16b457499b933d09b834d5d')
    request = ai.text_request()
    request.lang = 'es'  # optional, default value equal 'en'
    request.session_id = "ikarosid"
    request.query = texto

    response = request.getresponse()
    query = json.loads(response.read())

    print(query["result"]["parameters"])

    if query["result"]["fulfillment"]["speech"] != "":
    	tts.tts(query["result"]["fulfillment"]["speech"])


apiaiquery("da")