# Diagnostico y prueba de conectividad con Bots de Telegram
# Proyecto 2 - Sistemas Inteligentes (INFO1157)

import sys
import os
from pathlib import Path

# Aseguramos import de config
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

try:
    import telepot
except ImportError:
    telepot = None

from config import bots, es_modo_simulado, carpeta_reportes
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def enmascarar_token(token):
    if not token or len(token) < 10:
        return token
    return f"{token[:6]}...{token[-4:]}"

def probar_bot(cliente_id, datos_bot, enviar_foto=False):
    nombre = datos_bot['nombre']
    token = datos_bot['token']
    chat_id = datos_bot['chat_id']

    print(f"\n--- {nombre} ---")
    print(f"Token:   {enmascarar_token(token)}")
    print(f"Chat ID: {chat_id}")

    if es_modo_simulado(token):
        print(">> Estado: [MODO SIMULADO] Token no configurado.")
        print("   Para activar este bot, agrega el TOKEN real en el archivo .env o en config.py.")
        return False

    if telepot is None:
        print(">> Error: La libreria 'telepot' no esta instalada.")
        return False

    try:
        bot = telepot.Bot(token)
        info = bot.getMe()
        print(f">> Conexion exitosa con Telegram API!")
        print(f"   Nombre del Bot: {info.get('first_name')}")
        print(f"   Username:       @{info.get('username')}")
    except Exception as error_bot:
        print(f">> Error al autenticar con Telegram: {error_bot}")
        return False

    # Verificacion de Chat ID y envio de mensaje de prueba
    if not chat_id or chat_id.startswith('CHAT_ID_'):
        print(">> Chat ID no configurado.")
        try:
            updates = bot.getUpdates()
            if updates:
                ultimo = updates[-1]
                msg = ultimo.get('message', {})
                posible_id = msg.get('chat', {}).get('id')
                nombre_usuario = msg.get('from', {}).get('first_name', 'Usuario')
                print(f">> Se detecto un mensaje reciente de '{nombre_usuario}' con Chat ID: {posible_id}")
                print(f"   Puedes copiar este Chat ID en tu archivo .env o config.py: BOT_{cliente_id}_CHAT_ID={posible_id}")
            else:
                print("   Tip: Abre Telegram, busca tu bot (@" + str(info.get('username')) + ") y presiona 'Iniciar' o enviale un mensaje.")
        except Exception:
            pass
        return True

    # Enviar mensaje de prueba de texto
    try:
        texto_prueba = f"🔔 [Prueba de Conexion]\nHola! Este es un mensaje de prueba desde el {nombre} (Proyecto 2 - INFO1157)."
        bot.sendMessage(chat_id, texto_prueba)
        print(f">> Mensaje de texto de prueba enviado exitosamente a Chat ID: {chat_id}")
    except Exception as error_msg:
        print(f">> Error al enviar mensaje de texto a Chat ID {chat_id}: {error_msg}")
        return False

    # Enviar foto de prueba si se solicita
    if enviar_foto:
        try:
            ruta_prueba = carpeta_reportes / f"test_bot_{cliente_id}.png"
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot([1, 2, 3, 4, 5], [10, 25, 15, 30, 20], color='blue', label='Prueba')
            ax.set_title(f"Prueba de Grafico - {nombre}")
            ax.legend()
            fig.tight_layout()
            fig.savefig(ruta_prueba, dpi=100)
            plt.close(fig)

            with open(ruta_prueba, 'rb') as f:
                bot.sendPhoto(chat_id, f, caption=f"📊 Grafico de prueba enviado por {nombre}")
            print(f">> Foto de prueba enviada exitosamente a Telegram!")
        except Exception as error_foto:
            print(f">> Error al enviar foto de prueba: {error_foto}")

    return True

def main():
    print("========================================================")
    print("      DIAGNOSTICO Y PRUEBA DE BOTS DE TELEGRAM")
    print("========================================================")
    print("Este script verifica la validez de los tokens y la recepcion")
    print("de mensajes y graficos en Telegram.\n")

    enviar_foto = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--foto', '-f', 'foto']:
        enviar_foto = True

    bots_configurados = 0
    for id_cliente, datos in bots.items():
        if probar_bot(id_cliente, datos, enviar_foto=enviar_foto):
            bots_configurados += 1

    print("\n========================================================")
    print(f"Resumen: {bots_configurados}/4 bots verificados con exito.")
    if bots_configurados == 0:
        print("\nPara conectar tus bots reales:")
        print("1. En Telegram, abre @BotFather y usa /newbot para crear tu(s) bot(s).")
        print("2. Abre tu bot creado y presiona 'Iniciar' (/start).")
        print("3. Abre @userinfobot para conocer tu Chat ID numerico.")
        print("4. Copia los tokens y tu Chat ID en el archivo 'Proyecto2/.env'")
        print("   (Usa el archivo 'Proyecto2/.env.example' como guia).")
    print("========================================================\n")

if __name__ == '__main__':
    main()
