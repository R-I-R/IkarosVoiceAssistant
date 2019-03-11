import serial,time

arduinoPort = serial.Serial('/dev/ttyS0', 9600, timeout=1)
 
# Reset manual del Arduino
arduinoPort.setDTR(False)  
time.sleep(0.3)  
# Se borra cualquier data que haya quedado en el buffer
arduinoPort.flushInput()  
arduinoPort.setDTR()  
time.sleep(0.3)

while True:
    msg = input()
    if(msg == "salir"): break
    arduinoPort.write(msg.encode())
    m = arduinoPort.readline().decode()
    while m != '':
        m = arduinoPort.readline().decode()
        print(m)
arduinoPort.close()