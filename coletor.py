try:
    import serial
except ModuleNotFoundError:
    print("Erro: o módulo 'pyserial' não está instalado.")
    print("Instale com: python -m pip install pyserial")
    exit(1)

import json
import time
import os
from datetime import datetime

# Altere para a porta correta do seu Arduino (ex: 'COM3' no Windows ou '/dev/ttyUSB0' no Linux)
porta_serial = 'COM8'
baud_rate = 9600

try:
    arduino = serial.Serial(porta_serial, baud_rate, timeout=1)
    time.sleep(2) # Aguarda o Arduino resetar e iniciar
    print("Conectado ao Arduino com sucesso!")
except Exception as e:
    print(f"Erro ao conectar na porta {porta_serial}: {e}")
    exit()

dados_coletados = []

print("Coletando dados do DS18B20... Pressione Ctrl+C para encerrar e salvar.")

try:
    while True:
        if arduino.in_waiting > 0:
            linha = arduino.readline().decode('utf-8').strip()
            
            if linha == "FIM":
                print("Medição concluída pelo Arduino.")
                break

            partes = linha.split(",")
            if len(partes) != 2:
                continue

            try:
                tempo_segundos = int(partes[0].strip())
                temperatura = float(partes[1].strip())
            except ValueError:
                continue

            dados = {
                "tempo_segundos": tempo_segundos,
                "temperatura": temperatura,
                "timestamp": time.strftime("%H:%M:%S")
            }

            print(f"[{dados['timestamp']}] Tempo: {dados['tempo_segundos']} s, Temp: {dados['temperatura']} °C")
            dados_coletados.append(dados)

except KeyboardInterrupt:
    print("\nColeta interrompida pelo usuário.")

finally:
    if dados_coletados:
        # Cria pasta de backups
        backups_dir = "data_backups"
        os.makedirs(backups_dir, exist_ok=True)

        # Se existir um arquivo anterior, move para backups com timestamp
        if os.path.exists("dados_temperatura.json"):
            old_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                os.replace("dados_temperatura.json", os.path.join(backups_dir, f"dados_temperatura_{old_ts}.json"))
            except Exception:
                pass

        # Salva arquivo com timestamp e também atualiza 'dados_temperatura.json'
        new_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_ts = f"dados_temperatura_{new_ts}.json"
        try:
            with open(filename_ts, "w", encoding="utf-8") as arquivo_ts:
                json.dump(dados_coletados, arquivo_ts, indent=4, ensure_ascii=False)

            with open("dados_temperatura.json", "w", encoding="utf-8") as arquivo:
                json.dump(dados_coletados, arquivo, indent=4, ensure_ascii=False)

            print(f"Sucesso! {len(dados_coletados)} registros salvos em '{filename_ts}' e em 'dados_temperatura.json'.")
        except Exception as e:
            print(f"Erro ao salvar arquivos: {e}")
    else:
        print("Nenhum dado válido foi coletado.")
        
    arduino.close()