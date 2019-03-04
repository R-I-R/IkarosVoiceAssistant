//importar librerias
#include<Wire.h>
#include<SPI.h>
#include<NRFLite.h>
#include<EEPROM.h>

//Indice de IDs:                  publicas = 0-9
#define Central 10
#define LuzPieza 11
#define CortinasPieza 12

//defines
#define enviar(ID,dato) if(radio.send(ID,&dato, sizeof(dato))) Serial1.println("Error de Transmision")
#define cerrarcortina 5000   //4700
#define abrircortina 5200   //5200
#define pararcortina 85
#define velabrircortina 180
#define velcerrarcortina 10

#define bateria A0
#define rele 4
#define CE_PIN 10
#define CSN_PIN 9

//creacion de objetos
NRFLite radio;

//creacion de estructuras
struct SLuzPieza{
  int ID = LuzPieza;
  bool estado;
}SLuzPiezaDato;

struct SCortinasPieza{
  int ID = 12;
  byte pos;
  unsigned long pasos[2] = {cerrarcortina,abrircortina};
  byte parar = pararcortina;
  byte vel[2] = {velcerrarcortina,velabrircortina};
}CortinasPiezaDato;

//creacion de variables globales
bool enviadoLuzPieza;
byte packetSize;
bool avisocortinas = false;
int voltaje = 0;

//creacion de funciones

//inicio de codigo
void setup() {
  pinMode(bateria,INPUT);
  pinMode(rele,OUTPUT);

  Wire.begin(Central);
  Wire.onRequest(mandarCarga);
  
  Serial1.begin(9600);
  while(!Serial1) monitorearCarga();
  Serial1.setTimeout(50);
  
  if(radio.init(Central,CE_PIN,CSN_PIN))Serial1.println("Radio Online");//Radio ID, CE pin, CSN pin
  else Serial1.println("Error al conectar con el Radio");
}

void loop() {
  monitorearCarga();
  revisionRadio();
  revisionSerial();
  delay(100);
}

void revisionRadio(){
  packetSize = radio.hasData();

  if(packetSize == sizeof(SLuzPiezaDato)){
    radio.readData(&SLuzPiezaDato);
    if(SLuzPiezaDato.ID == LuzPieza){
      if(SLuzPiezaDato.estado){
        Serial1.println("luz prendida");
      }else{
        Serial1.println("luz apagada");
      }
    }
  }else if(packetSize == sizeof(CortinasPiezaDato)){
    radio.readData(&CortinasPiezaDato);
    if(!avisocortinas){
      if(CortinasPiezaDato.pos == 100) Serial1.println("Abriendo cortinas");
      else if(CortinasPiezaDato.pos == 0) Serial1.println("Cerrando cortinas");
      else{
        String temps = "Moviendo cortinas al ";
        temps += CortinasPiezaDato.pos;
        temps += "%";
        Serial1.println(temps);
      }
      avisocortinas = true;
    }else{
      if(CortinasPiezaDato.pos == 100) Serial1.println("Cortinas abiertas");
      else if(CortinasPiezaDato.pos == 0) Serial1.println("Cortinas Cerradas");
      else{
        String temps = "cortinas al ";
        temps += CortinasPiezaDato.pos;
        temps += "%";
        Serial1.println(temps);
      }
      avisocortinas = false;
    }
  }
}

void revisionSerial(){
  if(Serial1.available()){
    String serial = Serial1.readStringUntil('\n');
    //Serial1.print("----");
    //Serial1.println(serial);
    if(serial.equals("luz pieza on")){
      SLuzPiezaDato.estado = 1;
      enviar(LuzPieza,SLuzPiezaDato);
    }else if(serial.equals("luz pieza off")){
      SLuzPiezaDato.estado = 0;
      enviar(LuzPieza,SLuzPiezaDato);
    }else if(serial.equals("cortina pieza on")){
      CortinasPiezaDato.pos = 100;
      radio.send(CortinasPieza,&CortinasPiezaDato, sizeof(CortinasPiezaDato));
    }else if(serial.equals("cortina pieza off")){
      CortinasPiezaDato.pos = 0;
      radio.send(CortinasPieza,&CortinasPiezaDato, sizeof(CortinasPiezaDato));
    }else if(serial.substring(0,14).equals("cortina pieza ")){
      int x = serial.substring(14).toInt();
      delay(50);
      CortinasPiezaDato.pos = x;
      radio.send(CortinasPieza,&CortinasPiezaDato,sizeof(CortinasPiezaDato));
    }
  }
}

int monitorearCarga(){
  int lectura = 0;
  int voltajeT = 0;
 
  for(int a = 0; a < 10; a++){
    lectura = map(analogRead(bateria),0,1023,0,500);
    lectura -= round(8.5*lectura/100.0);
    voltajeT += lectura;
  }
  voltajeT /= 10;
  voltaje = voltajeT;

  if(voltaje < 410) digitalWrite(rele,HIGH);
  else digitalWrite(rele,LOW);

}

void mandarCarga(){
  byte data[] = {voltaje/100,voltaje%100};
  Wire.write(data,2);
}
