@echo off
rem Proyecto 2 - Publicador y suscriptores MQTT con visualizacion y Telegram
rem Menu interactivo segun pauta del profesor Alberto Caro

chcp 65001 > nul
cd /d "%~dp0"
title Sistema Distribuido MQTT (Mosquitto) - Proyecto 2

:menu
cls
echo --------------------------------------------------------
echo       PROYECTO 2 - SISTEMAS INTELIGENTES (INFO1157)
echo         Arquitectura de Publicacion y Suscripcion
echo --------------------------------------------------------
echo.
echo   [1] Iniciar Publicador de Datos (Caro)
echo   [2] Iniciar Clientes Suscriptores 1 al 4 (Ventanas independientes)
echo   [3] Iniciar Simulador Completo (Publicador + 4 Clientes)
echo   [4] Salir
echo.
echo   * Requiere Broker Mosquitto activo en 127.0.0.1:1883
echo --------------------------------------------------------
set /p opcion="Selecciona una opcion (1-4): "

if "%opcion%"=="1" goto publicador
if "%opcion%"=="2" goto suscriptores
if "%opcion%"=="3" goto simulador
if "%opcion%"=="4" goto salir

echo.
echo Opcion no valida. Intenta de nuevo.
timeout /t 2 > nul
goto menu

:publicador
cls
echo --------------------------------------------------------
echo Iniciando Publicador de Datos (Material Particulado y Clima)...
echo Presiona Ctrl+C para detener y volver al menu.
echo --------------------------------------------------------
echo.
python src\publicador.py
pause
goto menu

:suscriptores
cls
echo --------------------------------------------------------
echo Abriendo terminales independientes para los clientes 1 al 4...
echo --------------------------------------------------------
echo.
start "Cliente 1 - PM1.0" python src\cliente1.py
start "Cliente 2 - PM2.5" python src\cliente2.py
start "Cliente 3 - PM10" python src\cliente3.py
start "Cliente 4 - Clima" python src\cliente4.py
echo Las 4 terminales han sido iniciadas exitosamente.
echo.
pause
goto menu

:simulador
cls
echo --------------------------------------------------------
echo Iniciando Simulador Completo (Publicador + 4 Clientes)...
echo Presiona Ctrl+C para detener la simulacion ordenada.
echo --------------------------------------------------------
echo.
python src\simulador_completo.py
pause
goto menu

:salir
cls
echo Cerrando menu. Hasta luego!
timeout /t 1 > nul
exit /b
