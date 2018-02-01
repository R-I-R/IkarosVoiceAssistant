import speech_recognition as sr
import sys
import signal

sys.path.insert(1,"snowboy/")
import snowboydecoderIkarosrecorder as snowboydecoder
sys.path.insert(1,"tts/")
import tts

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

def reconocervoz():
	r = sr.Recognizer()
	m = sr.Microphone()
	with m as source:
	    tts.tts("Lo escucho")
	    r.adjust_for_ambient_noise(source)
	    audio = r.listen(source)
	try:
	    print("Google Speech Recognition thinks you said: " + r.recognize_google(audio,language="es-CL"))
	except sr.UnknownValueError:
	    print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
	    print("Could not request results from Google Speech Recognition service; {0}".format(e))

signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector("snowboy/models/Ikaros.pmdl",sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=reconocervoz,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()