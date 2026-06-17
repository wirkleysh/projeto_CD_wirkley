@echo off
REM Script para instalar bibliotecas do PlatformIO e compilar o projeto
cd /d "%~dp0\.."
set "PIO_CMD=pio"
if exist "%USERPROFILE%\.platformio\penv\Scripts\platformio.exe" (
  set "PIO_CMD=%USERPROFILE%\.platformio\penv\Scripts\platformio.exe"
)
echo Usando %PIO_CMD% para instalar bibliotecas...
"%PIO_CMD%" lib install "milesburton/DallasTemperature"
"%PIO_CMD%" lib install "paulstoffregen/OneWire"
echo Compilando o projeto...
"%PIO_CMD%" run
echo.
echo Concluido. Pressione qualquer tecla para fechar.
pause >nul
