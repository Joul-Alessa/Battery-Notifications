# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:23:01 2025

@author:
"""
#%% Manejo de librerías y de variables de entorno
# Librerías para el manejo de todo el programa
import psutil
import time
from playsound import playsound
from notifypy import Notify
import requests

# Librarías para evitar mostrar información sensible en el código
from dotenv import load_dotenv
import os

# Carga las variables de entorno del archivo .env
load_dotenv()

# Accede a las variables de entorno
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

#%% Código

# Función que manda mansaje a través de Telegram
def send_telegram_message(message):
    url = "https://api.telegram.org/bot" + str(TOKEN) + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("Error al enviar mensaje:", response.text)
#    else:
#        print("Mensaje enviado a Telegram con éxito.")        

# Función que manda la notificacion de sistema en PC
def send_notification(title, message):
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.send()

# Función general que revisa el estado de la batería
def check_battery_level():
    # Obtener información de la batería
    battery = psutil.sensors_battery()
    if battery is not None:
        level = battery.percent
        plugged = battery.power_plugged
        
        # Verificar el nivel de la batería y si está conectada a la corriente
        if level <= 20 and not plugged:
            titleNotif = "Alerta de Batería"
            messageNotif = f"⚠️ Nivel de batería bajo ({level} %). \nConecta el cargador."
            send_notification(titleNotif, messageNotif)
            send_telegram_message(messageNotif)
            playsound("sounds/battery-low.mp3")
            
            time.sleep(80)
        elif level >= 90 and plugged:
            #Envia notificacion de sistema
            titleNotif = "Alerta de Batería"
            messageNotif = f"⚡ Batería casi llena ({level} %). \nConsidera desconectar el cargador."
            send_notification(titleNotif, messageNotif)
            send_telegram_message(messageNotif)
            playsound("sounds/battery-high.mp3")
            
            time.sleep(80)
    else:
        print("No se pudo obtener información sobre la batería.")
        exit()

# ciclo para revisar el nivel de la batería
def main():
    while True:
        check_battery_level()
        time.sleep(10)  # Espera 10 segundos antes de volver a comprobar

if __name__ == "__main__":
    main()