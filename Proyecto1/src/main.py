# Ejecutable principal del simulador inercial 3D
# Proyecto 1 - Sistemas Inteligentes

import os
import sys

# Agregamos la carpeta src al path por si se corre desde afuera
directorio_script = os.path.dirname(os.path.abspath(__file__))
if directorio_script not in sys.path:
    sys.path.insert(0, directorio_script)

from vpython import rate, color
from decoder import cargar_archivo
from visualizer import (
    iniciar_escena,
    Get_Frame,
    orientar_absoluto,
    reiniciar_orientacion,
    actualizar_hud,
    agregar_botones
)

# Variables de control del reproductor
pausado = False
paso_adelante = False
paso_atras = False
velocidad = 1.0
reiniciar = False

indice = 0
total_tramas = 0
tramas = []
cubo = None
hud = None

def buscar_archivo_binario(nombre='inercial.bin'):
    # Busca el archivo en las rutas tipicas
    rutas = [
        os.path.join(directorio_script, '..', 'data', nombre),
        os.path.join(directorio_script, 'data', nombre),
        os.path.join(directorio_script, nombre),
        os.path.join('Proyectos', 'Proyecto1', 'data', nombre),
        os.path.join('data', nombre),
        nombre
    ]
    for r in rutas:
        if os.path.exists(r):
            return os.path.abspath(r)
    return None

# Funciones que ejecutan los botones y el teclado
def accion_pausa(evt=None):
    global pausado
    pausado = not pausado
    print(f"[Control] {'Pausado' if pausado else 'Reanudado'}")
    refrescar_pantalla()

def accion_avanzar(evt=None):
    global pausado, paso_adelante
    pausado = True
    paso_adelante = True

def accion_retroceder(evt=None):
    global pausado, paso_atras
    pausado = True
    paso_atras = True

def accion_reiniciar(evt=None):
    global reiniciar
    reiniciar = True

def accion_vel1(evt=None):
    global velocidad
    velocidad = 1.0
    print("[Control] Velocidad normal (1.0x)")
    refrescar_pantalla()

def accion_vel2(evt=None):
    global velocidad
    velocidad = 2.0
    print("[Control] Velocidad rapida (2.0x)")
    refrescar_pantalla()

def refrescar_pantalla():
    if 0 <= indice < total_tramas and hud:
        d = tramas[indice]
        actualizar_hud(hud, d['roll'], d['pitch'], d['yaw'], indice + 1, total_tramas, pausado, velocidad)

def manejar_teclado(evt):
    tecla = evt.key

    if tecla in (' ', 'space', 'Spacebar'):
        accion_pausa()
    elif tecla in ('right', 'Right', 't', 'T'):
        accion_avanzar()
    elif tecla in ('left', 'Left', 'b', 'B'):
        accion_retroceder()
    elif tecla in ('r', 'R'):
        accion_reiniciar()
    elif tecla == '1':
        accion_vel1()
    elif tecla == '2':
        accion_vel2()

def main():
    global pausado, paso_adelante, paso_atras, velocidad, reiniciar, indice
    global total_tramas, tramas, cubo, hud

    # 1. Buscamos y cargamos el archivo con las tramas
    ruta_bin = buscar_archivo_binario('inercial.bin')
    if not ruta_bin:
        print("Error: No se encontro el archivo inercial.bin")
        return

    tramas = cargar_archivo(ruta_bin)
    total_tramas = len(tramas)
    if total_tramas == 0:
        print("El archivo binario no tiene tramas validas.")
        return

    validas = sum(1 for t in tramas if t['checksum_valido'])
    print(f"Archivo cargado: {ruta_bin}")
    print(f"Total tramas: {total_tramas} ({validas}/{total_tramas} checksums OK)")
    print("\nControles:")
    print("  [Espacio]       : Pausa / Play")
    print("  [Flecha Izq / B]: Retroceder 1 trama")
    print("  [Flecha Der / T]: Avanzar 1 trama")
    print("  [1] / [2]       : Velocidad 1x / 2x")
    print("  [R]             : Reiniciar simulacion\n")

    # 2. Inicializamos la ventana 3D y el cubo rojo
    escena, base, hud = iniciar_escena(titulo='Kinect 3D - Simulador Inercial')
    cubo = Get_Frame((0, 0, 0), color.red)

    # Conectamos el teclado y la botonera interactiva
    escena.bind('keydown', manejar_teclado)
    agregar_botones({
        'atras': accion_retroceder,
        'pausa': accion_pausa,
        'adelante': accion_avanzar,
        'reiniciar': accion_reiniciar,
        'vel1': accion_vel1,
        'vel2': accion_vel2
    })

    # Mostramos la primera trama
    refrescar_pantalla()

    # 3. Bucle principal de reproduccion
    indice = 0
    while True:
        # Tasa de refresco segun la velocidad
        if not pausado:
            rate(10 * velocidad)
        else:
            rate(25)

        # Si el usuario pidio reiniciar
        if reiniciar:
            reiniciar_orientacion(cubo)
            indice = 0
            reiniciar = False
            paso_adelante = False
            paso_atras = False
            refrescar_pantalla()
            print("[Control] Simulacion reiniciada a trama 1")
            continue

        # Si se apreto retroceder
        if paso_atras:
            paso_atras = False
            if indice > 0:
                indice -= 1
                d = tramas[indice]
                orientar_absoluto(cubo, d['roll'], d['pitch'], d['yaw'])
                refrescar_pantalla()
                print(f"[{indice + 1:03d}/{total_tramas:03d}] (Atras) Roll: {d['roll']:+6.2f} | Pitch: {d['pitch']:+6.2f} | Yaw: {d['yaw']:+6.2f}")
            continue

        # Si ya llego al final y no esta en retroceso
        if indice >= total_tramas:
            continue

        # Avance normal o paso a paso
        if not pausado or paso_adelante:
            d = tramas[indice]
            cs_texto = "OK" if d['checksum_valido'] else "FAIL"

            orientar_absoluto(cubo, d['roll'], d['pitch'], d['yaw'])
            actualizar_hud(hud, d['roll'], d['pitch'], d['yaw'], indice + 1, total_tramas, pausado, velocidad)
            print(f"[{indice + 1:03d}/{total_tramas:03d}] Roll: {d['roll']:+6.2f} | Pitch: {d['pitch']:+6.2f} | Yaw: {d['yaw']:+6.2f} | CS: {cs_texto}")

            paso_adelante = False
            indice += 1

# ----------------------------------------------------------------------
# Codigo para conectar el sensor fisico por Bluetooth en laboratorio
# (segun el ejemplo del examen del profe Alberto Caro con RS.Serial):
# ----------------------------------------------------------------------
# import serial as RS
# import struct as ST
#
# def leer_bluetooth():
#     # COM9 a 115200 baudios
#     puerto = RS.Serial('COM9', 115200, timeout=1)
#     while True:
#         cabecera = puerto.read(2)
#         if len(cabecera) == 2 and cabecera[0] == 0x55 and cabecera[1] == 0x53:
#             resto = puerto.read(9)
#             if len(resto) == 9:
#                 trama_completa = cabecera + resto
#                 # verificamos checksum
#                 if (sum(trama_completa[:10]) & 0xFF) == trama_completa[10]:
#                     roll_raw = ST.unpack('<h', trama_completa[2:4])[0]
#                     pitch_raw = ST.unpack('<h', trama_completa[4:6])[0]
#                     yaw_raw = ST.unpack('<h', trama_completa[6:8])[0]
#                     roll = (roll_raw / 32768.0) * 180.0
#                     pitch = (pitch_raw / 32768.0) * 180.0
#                     yaw = (yaw_raw / 32768.0) * 180.0
#                     print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")

if __name__ == '__main__':
    main()
