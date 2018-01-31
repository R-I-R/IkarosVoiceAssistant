#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
from wit import Wit

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    #r.energy_threshold =  4000
    print(source)
    r.adjust_for_ambient_noise(source)
    audio = r.listen(source)

print("listo")
 #recognize speech using Sphinx
#try:
#    print("Sphinx thinks you said: " + r.recognize_sphinx(audio))
#except sr.UnknownValueError:
#    print("Sphinx could not understand audio")
#except sr.RequestError as e:
#    print("Sphinx error; {0}".format(e))

# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said: " + r.recognize_google(audio,language="es-CL"))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

# recognize speech using Google Cloud Speech
#GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
#try:
#    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
#except sr.UnknownValueError:
#    print("Google Cloud Speech could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Google Cloud Speech service; {0}".format(e))

# recognize speech using Wit.ai
WIT_AI_KEY = "4H77AN3UNF7WLRNM5WNO66IDLAAKMCDZ"  # Wit.ai keys are 32-character uppercase alphanumeric strings
try:
    #user = Wit(WIT_AI_KEY)
    print("Wit.ai thinks you said: " + r.recognize_wit(audio, key=WIT_AI_KEY))
    #print(user.message(r.recognize_wit(audio, key=WIT_AI_KEY)))
except sr.UnknownValueError:
    print("Wit.ai could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Wit.ai service; {0}".format(e))

# recognize speech using Microsoft Bing Voice Recognition
BING_KEY = "e124560f79fc46698e917f77f134242b"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings '35666e3c96234af4b3ebacfb3e2aa28c' clave 2
try:
    print("Microsoft Bing Voice Recognition thinks you said: " + r.recognize_bing(audio, key=BING_KEY,language="es-ES"))
except sr.UnknownValueError:
    print("Microsoft Bing Voice Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

# recognize speech using Houndify
#HOUNDIFY_CLIENT_ID = "INSERT HOUNDIFY CLIENT ID HERE"  # Houndify client IDs are Base64-encoded strings
#HOUNDIFY_CLIENT_KEY = "INSERT HOUNDIFY CLIENT KEY HERE"  # Houndify client keys are Base64-encoded strings
#try:
#    print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
#except sr.UnknownValueError:
#    print("Houndify could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Houndify service; {0}".format(e))

# recognize speech using IBM Speech to Text
IBM_USERNAME = "5f1c624e-5803-449f-bd64-e2c99e7f9a36"  # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "OKcadVtzcs5N"  # IBM Speech to Text passwords are mixed-case alphanumeric strings
try:
    print("IBM Speech to Text thinks you said: " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD,language="es-ES"))
except sr.UnknownValueError:
    print("IBM Speech to Text could not understand audio")
except sr.RequestError as e:
    print("Could not request results from IBM Speech to Text service; {0}".format(e))
    

#CLIENT_ACCESS_TOKEN_APIAI = 'f197e55e5cff4bec9c6ed33f477f58af'
#SESSION_ID = "8a54ca28-e5e5-435d-99de-76f6bef1e35d"
#try:
#    print("ApiAi cree que dices: "+r.recognize_api(audio,client_access_token=CLIENT_ACCESS_TOKEN_APIAI, language="es"))
#except sr.UnknownValueError:
#    print("ApiAi could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from ApiAi service; {0}".format(e))