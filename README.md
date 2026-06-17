# Controle Discreto — instruções rápidas

Para instalar as bibliotecas necessárias e compilar o projeto, execute o script criado no diretório do projeto:

Windows (PowerShell ou CMD):

```powershell
cd "C:\Users\wirkl\Documents\PlatformIO\Projects\controle_discreto"
scripts\install_libs.bat
```

Ou rode manualmente:

```powershell
pio lib install "milesburton/DallasTemperature"
pio lib install "paulstoffregen/OneWire"
pio run
```

Se o `pio` não for reconhecido, instale o PlatformIO CLI ou use a extensão PlatformIO no VS Code. Você também pode usar o executável direto do PlatformIO:

```powershell
"%USERPROFILE%\.platformio\penv\Scripts\platformio.exe" run
```

## Gerar arquivo de dados

Depois de enviar o código para o Arduino, abra um terminal no diretório do projeto e execute:

```powershell
python coletor.py
```

O script `coletor.py` lê os dados enviados pelo Arduino no formato `tempo,temperatura` e salva em `dados_temperatura.json`.

O Arduino agora roda por 30 minutos e, ao final deste período, para automaticamente.

Se precisar, instale o PySerial com:

```powershell
python -m pip install pyserial
```
