//importar librerias
#include<SPI.h>
#include<NRFLite.h>
#include<EEPROM.h>

//Indice de IDs:                  publicas = 0-9
#define Central 10
#define LuzPieza 11
#define CortinasPieza 12

//defines
#define enviar(ID,dato) if(radio.send(ID,&dato, sizeof(dato))) Serial.println("Error de Transmicion")
#define cerrarcortina 5000   //4700
#define abrircortina 5200   //5200
#define pararcortina 85
#define velabrircortina 180
#define velcerrarcortina 10

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
  unsigned long limites[2] = {cerrarcortina,abrircortina};
  byte parar = pararcortina;
  byte vel[2] = {velcerrarcortina,velabrircortina};
}CortinasPiezaDato;

//creacion de variables globales
bool enviadoLuzPieza;
byte packetSize;
bool avisocortinas = false;

//creacion de funciones

//inicio de codigo
void setup() {
  pinMode(10,OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(50);
  if(radio.init(10,5,6))Serial.println("Radio Online");//Radio ID, CE pin, CSN pin
  else Serial.println("Error al conectar con el Radio");
}

void loop() {
  
  packetSize = radio.hasData();

  if(packetSize == sizeof(SLuzPiezaDato)){
    radio.readData(&SLuzPiezaDato);
    if(SLuzPiezaDato.ID == LuzPieza){
      if(SLuzPiezaDato.estado){
        Serial.println("luz prendida");
      }else{
        Serial.println("luz apagada");
      }
    }
  }else if(packetSize == sizeof(CortinasPiezaDato)){
    radio.readData(&CortinasPiezaDato);
    if(!avisocortinas){
      Serial.println("...");
      avisocortinas = true;
    }else{
      if(CortinasPiezaDato.pos) Serial.println("Cortinas Abiertas");
      else Serial.println("Cortinas Cerradas");
      avisocortinas = false;
    }
  }
  

  
  if(Serial.available()){
    String serial = Serial.readString();
    if(serial.equals("prender luces pieza")){
      Serial.println("prendiendo luces");
      SLuzPiezaDato.estado = 1;
      enviar(LuzPieza,SLuzPiezaDato);
    }else if(serial.equals("apagar luces pieza")){
      Serial.println("apagando luces");
      SLuzPiezaDato.estado = 0;
      enviar(LuzPieza,SLuzPiezaDato);
    }else if(serial.equals("abrir cortinas pieza")){
      Serial.print("Abriendo cortinas");
      CortinasPiezaDato.pos = 100;
      radio.send(CortinasPieza,&CortinasPiezaDato, sizeof(CortinasPiezaDato));
    }else if(serial.equals("cerrar cortinas pieza")){
      Serial.print("cerrando cortinas");
      CortinasPiezaDato.pos = 0;
      radio.send(CortinasPieza,&CortinasPiezaDato, sizeof(CortinasPiezaDato));
    }else if(serial.substring(0,18).equals("cortinas pieza al ")){
      int x = serial.substring(18).toInt();
      delay(50);
      Serial.print("Moviendo cortinas al ");Serial.print(x);Serial.print("%");
      CortinasPiezaDato.pos = x;
      radio.send(CortinasPieza,&CortinasPiezaDato,sizeof(CortinasPiezaDato));
    }
  }
 }
