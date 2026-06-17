#include <OneWire.h>
#include <DallasTemperature.h>

// O pino de dados do sensor está ligado na porta digital 2 do Arduino
#define DADOS_PINO 12
#define MOSFET_PINO 6

// Cria uma instância da biblioteca OneWire para se comunicar com o sensor
OneWire oneWire(DADOS_PINO);

// Passa a referência do OneWire para a biblioteca DallasTemperature
DallasTemperature sensores(&oneWire);

const unsigned long TEMPO_TOTAL_MS = 90UL * 60UL * 1000UL; // 90 minutos
unsigned long tempoInicial;
bool medicaoConcluida = false;

void setup() {
  Serial.begin(9600);
  sensores.begin();
  sensores.setWaitForConversion(false); // Conversão não bloqueante
  sensores.requestTemperatures(); // Inicia primeira conversão
  tempoInicial = millis();
  pinMode(MOSFET_PINO, OUTPUT);
}

void loop() {
  unsigned long tempoDecorridoMs = millis() - tempoInicial;
  unsigned long tempoSegundos = tempoDecorridoMs / 1000UL;

  if (tempoDecorridoMs >= TEMPO_TOTAL_MS) {
    if (!medicaoConcluida) {
      analogWrite(MOSFET_PINO, 0);
      Serial.println("FIM");
      medicaoConcluida = true;
    };
    return;
  }

  float razao = 0.5;
  analogWrite(MOSFET_PINO, razao * 255);

  float temperaturaC = sensores.getTempCByIndex(0);
  sensores.requestTemperatures(); // Inicia próxima conversão não bloqueante

  if (temperaturaC != DEVICE_DISCONNECTED_C) {
    Serial.print(tempoSegundos);
    Serial.print(",");
    Serial.println(temperaturaC, 2);
  }

  delay(1000); // Coleta dados a cada 1 segundo
}


