import speech_recognition as sr
import sys
import signal

sys.path.insert(1,"snowboy/")
import snowboydecoderIkaros as snowboydecoder

signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector("snowboy/models/Ikaros.pmdl",sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder.play_audio_file,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()