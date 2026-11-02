@echo off
rem Proyecto 2 - Publicador y suscriptores MQTT con visualizacion y Telegram
rem Menu interactivo para ejecutar broker, publicador, clientes, simulador o pruebas

chcp 65001 > nul
cd /d "%~dp0"
title Sistema Distribuido MQTT - Proyecto 2

:menu
cls
echo --------------------------------------------------------
echo       PROYECTO 2 - SISTEMAS INTELIGENTES (INFO1157)
echo         Arquitectura de Publicacion y Suscripcion
echo --------------------------------------------------------
echo.
echo   [1] Estado y Verificacion del Broker MQTT (Mosquitto)
echo   [2] Iniciar Publicador de Datos (Dr. Alberto Caro)
echo   [3] Iniciar Clientes Suscriptores 1 al 4 (Ventanas separadas)
echo   [4] Iniciar Simulador Completo (Todo en uno)
echo   [5] Diagnostico y Prueba de Bots de Telegram
echo   [6] Salir
echo.
echo --------------------------------------------------------
set /p opcion="Selecciona una opcion (1-6): "

if "%opcion%"=="1" goto broker
if "%opcion%"=="2" goto publicador
if "%opcion%"=="3" goto suscriptores
if "%opcion%"=="4" goto simulador
if "%opcion%"=="5" goto telegram
if "%opcion%"=="6" goto salir

echo.
echo Opcion no valida. Intenta de nuevo.
timeout /t 2 > nul
goto menu

:broker
cls
echo --------------------------------------------------------
echo Verificando estado del Broker MQTT en 127.0.0.1:1883...
echo --------------------------------------------------------
echo.
python src\broker_local.py
pause
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
echo Iniciando Simulador Completo (Broker + Publicador + 4 Clientes)...
echo Presiona Ctrl+C para detener la simulacion ordenada.
echo --------------------------------------------------------
echo.
python src\simulador_completo.py
pause
goto menu

:telegram
cls
echo --------------------------------------------------------
echo Diagnostico y Prueba de Conexion con Bots de Telegram...
echo --------------------------------------------------------
echo.
python src\test_telegram.py
pause
goto menu

:salir
cls
echo Cerrando menu. Hasta luego!
timeout /t 1 > nul
exit /b
