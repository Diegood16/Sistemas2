# Decodificador de datos del sensor inercial (inercial.bin)
# Sistemas Inteligentes - Proyecto 1

import os
import struct
import ctypes as ct

# Estructura de 11 bytes que pide el profe con ctypes
class eTrama(ct.Structure):
    _fields_ = [
        ('B0', ct.c_ubyte), ('B1', ct.c_ubyte), ('B2', ct.c_ubyte),
        ('B3', ct.c_ubyte), ('B4', ct.c_ubyte), ('B5', ct.c_ubyte),
        ('B6', ct.c_ubyte), ('B7', ct.c_ubyte), ('B8', ct.c_ubyte),
        ('B9', ct.c_ubyte), ('BA', ct.c_ubyte)
    ]

def validar_checksum(trama):
    # Suma de los primeros 10 bytes truncada a 8 bits (modulo 256)
    suma = (
        trama.B0 + trama.B1 + trama.B2 + trama.B3 + trama.B4 +
        trama.B5 + trama.B6 + trama.B7 + trama.B8 + trama.B9
    ) & 0xFF
    return suma == trama.BA

def decodificar_angulos(trama):
    # Revisamos que sea cabecera 0x55 y paquete 0x53 (angulos de Euler)
    if trama.B0 != 0x55 or trama.B1 != 0x53:
        return None

    checksum_ok = validar_checksum(trama)

    # Convertimos los bytes a enteros con signo de 16 bits (little endian)
    raw_roll = struct.unpack('<h', bytes([trama.B2, trama.B3]))[0]
    raw_pitch = struct.unpack('<h', bytes([trama.B4, trama.B5]))[0]
    raw_yaw = struct.unpack('<h', bytes([trama.B6, trama.B7]))[0]
    raw_temp = struct.unpack('<h', bytes([trama.B8, trama.B9]))[0]

    # Formula del datasheet: (raw / 32768.0) * 180.0
    roll = (raw_roll / 32768.0) * 180.0
    pitch = (raw_pitch / 32768.0) * 180.0
    yaw = (raw_yaw / 32768.0) * 180.0
    temperatura = (raw_temp / 340.0) + 36.53

    return {
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw,
        'temperatura': temperatura,
        'checksum_valido': checksum_ok
    }

def cargar_archivo(ruta):
    # Leemos el binario de 11 en 11 bytes
    lista_tramas = []
    if not os.path.exists(ruta):
        print(f"No encontre el archivo: {ruta}")
        return lista_tramas

    tamano = ct.sizeof(eTrama)
    with open(ruta, 'rb') as f:
        indice = 0
        while True:
            bloque = f.read(tamano)
            if len(bloque) < tamano:
                break

            trama = eTrama.from_buffer_copy(bloque)
            datos = decodificar_angulos(trama)
            if datos:
                datos['indice'] = indice
                lista_tramas.append(datos)
            indice += 1

    return lista_tramas

if __name__ == '__main__':
    # Probamos leer el archivo directamente
    directorio = os.path.dirname(os.path.abspath(__file__))
    posibles_rutas = [
        os.path.join(directorio, '..', 'data', 'inercial.bin'),
        os.path.join('data', 'inercial.bin'),
        'inercial.bin'
    ]

    ruta_bin = next((r for r in posibles_rutas if os.path.exists(r)), 'inercial.bin')
    print("Probando decodificador...")
    tramas = cargar_archivo(ruta_bin)
    print(f"Total de tramas leidas: {len(tramas)}")

    validas = sum(1 for t in tramas if t['checksum_valido'])
    print(f"Tramas con checksum correcto: {validas}/{len(tramas)}")

    print("\nPrimeras 3 tramas:")
    for t in tramas[:3]:
        print(f"Trama {t['indice']}: Roll={t['roll']:.2f}, Pitch={t['pitch']:.2f}, Yaw={t['yaw']:.2f}")
