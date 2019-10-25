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
#define enviar(ID,dato) if(radio.send(ID,&dato, sizeof(dato))) Serial.println("Error de Transmision")
#define cerrarcortina 5000   //4700
#define abrircortina 5200   //5200
#define pararcortina 80
#define velabrircortina 180
#define velcerrarcortina 10

#define bateria A0
#define rele 4
#define CE_PIN 9
#define CSN_PIN 10

#define VCC 396

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
  
  Serial.begin(9600);
  while(!Serial) monitorearCarga();
  Serial.setTimeout(50);
  
  if(radio.init(Central,CE_PIN,CSN_PIN))Serial.println("Radio Online");//Radio ID, CE pin, CSN pin
  else Serial.println("Error al conectar con el Radio");
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
        Serial.println("luz prendida");
      }else{
        Serial.println("luz apagada");
      }
    }
  }else if(packetSize == sizeof(CortinasPiezaDato)){
    radio.readData(&CortinasPiezaDato);
    if(!avisocortinas){
      if(CortinasPiezaDato.pos == 100) Serial.println("Abriendo cortinas");
      else if(CortinasPiezaDato.pos == 0) Serial.println("Cerrando cortinas");
      else{
        String temps = "Moviendo cortinas al ";
        temps += CortinasPiezaDato.pos;
        temps += "%";
        Serial.println(temps);
      }
      avisocortinas = true;
    }else{
      if(CortinasPiezaDato.pos == 100) Serial.println("Cortinas abiertas");
      else if(CortinasPiezaDato.pos == 0) Serial.println("Cortinas Cerradas");
      else{
        String temps = "cortinas al ";
        temps += CortinasPiezaDato.pos;
        temps += "%";
        Serial.println(temps);
      }
      avisocortinas = false;
    }
  }
}

void revisionSerial(){
  if(Serial.available()){
    String serial = Serial.readStringUntil('\n');
    //Serial.print("----");
    //Serial.println(serial);
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
  float lectura = 0;
 
  for(int a = 0; a < 10; a++)
    lectura += analogRead(bateria);

  lectura /= 10;
  lectura = (lectura * VCC) / 1024;
  voltaje = lectura;
}

void mandarCarga(){
  byte data[] = {voltaje/100,voltaje%100};
  Wire.write(data,2);
}
