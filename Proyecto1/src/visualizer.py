# Visualizador 3D con VPython
# Proyecto 1 - Sistemas Inteligentes

import math
from vpython import canvas, box, vector, color, compound, label, button

# Indices de ejes
ROLL = 0   # Eje X
PITCH = 1  # Eje Y
YAW = 2    # Eje Z

def iniciar_escena(titulo='Kinect', ancho=1000, alto=750):
    # Creamos la ventana 3D con fondo negro
    escena = canvas(
        title=f"<b>{titulo}</b> - Sistemas Inteligentes",
        width=ancho,
        height=alto,
        center=vector(0, 0, 0),
        background=vector(0, 0, 0),
        forward=vector(-0.6, -0.4, -0.8),
        up=vector(0, 1, 0)
    )

    # El plano azul del suelo que pide el profe
    base = box(pos=vector(0, -150, 0), size=vector(500, 3, 500), color=color.blue)

    # Texto en pantalla para mostrar los angulos
    hud = label(
        pos=vector(0, 180, 0),
        text="Iniciando simulador...",
        height=13,
        font="monospace",
        color=color.white,
        box=True,
        opacity=0.7
    )

    return escena, base, hud

def Get_Frame(posicion=(0, 0, 0), color_cubo=color.red):
    # Armamos el sensor: caja roja y los dos ejes de referencia (azul y verde)
    pos_vec = vector(*posicion) if isinstance(posicion, (tuple, list)) else posicion

    caja = box(pos=pos_vec, size=vector(100, 60, 160), color=color_cubo)
    eje_azul = box(pos=pos_vec, size=vector(200, 2, 2), color=color.blue)
    eje_verde = box(pos=pos_vec, size=vector(2, 200, 2), color=color.green)

    # Agrupamos todo en un solo objeto solido para que rote junto
    modelo = compound([caja, eje_azul, eje_verde], origin=pos_vec)

    # Guardamos la orientacion original para poder resetear o rotar sin drift
    modelo.eje_original = vector(modelo.axis.x, modelo.axis.y, modelo.axis.z)
    modelo.up_original = vector(modelo.up.x, modelo.up.y, modelo.up.z)

    return modelo

def Rota(eje, angulo_rad, objeto):
    # Rota el objeto en el eje correspondiente
    if not objeto or angulo_rad == 0:
        return

    if eje == ROLL:
        vector_eje = vector(1, 0, 0)
    elif eje == PITCH:
        vector_eje = vector(0, 1, 0)
    elif eje == YAW:
        vector_eje = vector(0, 0, 1)
    else:
        return

    objeto.rotate(angle=angulo_rad, axis=vector_eje, origin=objeto.pos)

def orientar_absoluto(objeto, roll_deg, pitch_deg, yaw_deg):
    # Volvemos a la pose inicial y rotamos en orden Z-Y-X (Yaw, Pitch, Roll)
    # Asi podemos avanzar o retroceder sin que se deforme o acumule error
    if not objeto:
        return

    objeto.axis = vector(objeto.eje_original.x, objeto.eje_original.y, objeto.eje_original.z)
    objeto.up = vector(objeto.up_original.x, objeto.up_original.y, objeto.up_original.z)

    if yaw_deg != 0:
        Rota(YAW, math.radians(yaw_deg), objeto)
    if pitch_deg != 0:
        Rota(PITCH, math.radians(pitch_deg), objeto)
    if roll_deg != 0:
        Rota(ROLL, math.radians(roll_deg), objeto)

def reiniciar_orientacion(objeto):
    # Deja el cubo derecho en 0,0,0
    orientar_absoluto(objeto, 0, 0, 0)

def actualizar_hud(hud, roll, pitch, yaw, trama_actual, total_tramas, pausado, velocidad):
    # Actualiza el cartel con los datos actuales
    estado = "PAUSA" if pausado else "PLAY"
    hud.text = (
        f"Trama: {trama_actual}/{total_tramas}  [{estado} | {velocidad:.1f}x]\n"
        f"Roll : {roll:+6.2f}°\n"
        f"Pitch: {pitch:+6.2f}°\n"
        f"Yaw  : {yaw:+6.2f}°"
    )

def agregar_botones(acciones):
    # Agrega la botonera debajo de la ventana
    button(text="⏪ Retroceder", bind=acciones.get('atras'))
    button(text="⏯️ Pausa/Play", bind=acciones.get('pausa'))
    button(text="⏩ Avanzar", bind=acciones.get('adelante'))
    button(text="🔄 Reiniciar", bind=acciones.get('reiniciar'))
    button(text="1.0x", bind=acciones.get('vel1'))
    button(text="2.0x", bind=acciones.get('vel2'))
