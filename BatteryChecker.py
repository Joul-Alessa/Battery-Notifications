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
import sys
import json
from SMWinservice import SMWinservice
import wmi
import pythoncom

# Librarías para evitar mostrar información sensible en el código
from dotenv import load_dotenv
import os

#%% Código

# Crear conexión WMI
c = wmi.WMI()

# Suscribirse a cambios en la clase Win32_Battery
watcher = c.watch_for(
    notification_type="Modification",
    wmi_class="Win32_Battery"
)

class BatteryChecker(SMWinservice):
    _svc_name_ = "BatteryChecker"
    _svc_display_name_ = "Battery Notification Service"
    _svc_description_ = "Python Service that monitors the battery level status"
    args = {}
    TOKEN = ""
    CHAT_ID = ""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def start(self):
        # Carga las variables de entorno del archivo .env
        load_dotenv(os.path.join(BatteryChecker.BASE_DIR, ".env"))

        # Se accede a la información del json y se guardas su infomación
        try:
            with open(os.path.join(BatteryChecker.BASE_DIR, 'conf.json'), 'r') as file:
                BatteryChecker.args = json.load(file)
        except FileNotFoundError:
            print("Error: The file was not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            sys.exit(1)

        # Accede a las variables de entorno
        BatteryChecker.TOKEN = os.getenv("TOKEN")
        BatteryChecker.CHAT_ID = os.getenv("CHAT_ID")
        self.isrunning = True
    
    def restart(self):
        self.isrunning = False
        self.start()

    # Función que revisa cuando el archivo está por ser interrumpido (para las suspensiones y apagados)
    def stop(self):
        self.isrunning = False
        if BatteryChecker.args['closing']:
            battery = psutil.sensors_battery()
            level = battery.percent
            plugged = battery.power_plugged
            if plugged == True:
                messageNotif = f"ℹ️ El programa dejará de monitorear el nivel de batería ({level} %). Desenchufar"
            else:
                messageNotif = f"ℹ️ El programa dejará de monitorear el nivel de batería ({level} %)."
            self.send_telegram_message(messageNotif)

    # ciclo para revisar el nivel de la batería por medio de eventos
    def main(self):
        detection = False
        while self.isrunning:
            if (detection):
                time.sleep(BatteryChecker.args['sleepTime'])
                detection = False
            else:
                pythoncom.PumpWaitingMessages()  # Necesario para el hilo COM
                battery = watcher()  # Espera evento
                level = battery.EstimatedChargeRemaining
                status = battery.BatteryStatus  # 1 = descargando, 2 = cargando,

                if level <= BatteryChecker.args['lower'] and status == 1:
                    titleNotif = "Alerta de Batería"
                    messageNotif = f"⚠️ Nivel de batería bajo ({level} %). \nConecta el cargador."
                    self.send_notification(titleNotif, messageNotif)
                    self.send_telegram_message(messageNotif)
                    self.play_notification_sound("battery-low.mp3")
                    detection = True
                elif level >= BatteryChecker.args['higher'] and status == 2:
                    titleNotif = "Alerta de Batería"
                    messageNotif = f"⚡ Batería casi llena ({level} %). \nConsidera desconectar el cargador."
                    self.send_notification(titleNotif, messageNotif)
                    self.send_telegram_message(messageNotif)
                    self.play_notification_sound("battery-high.mp3")
                    detection = True
    
    # Función que manda mansaje a través de Telegram
    def send_telegram_message(self,message):
        if BatteryChecker.args['msgTelegram']:
            url = "https://api.telegram.org/bot" + str(BatteryChecker.TOKEN) + "/sendMessage"
            payload = {
                "chat_id": BatteryChecker.CHAT_ID,
                "text": message
            }
            
            try:
                requests.post(url, json=payload)
            except requests.ConnectionError as e:
                print(f"Error de conexión: {e}")
            except requests.Timeout as e:
                print(f"Error de tiempo de espera: {e}")
            except requests.RequestException as e:
                print(f"Error general de requests: {e}")

    # Función que manda la notificacion de sistema en PC
    def send_notification(title, message):
        #Señal a la GUI para disparar la notificación con su información correspondiente
        wenas=0

    # Función que reproduce el sonido para la notifiaciones de sistema en PC
    def play_notification_sound(sound_file_name):
        if BatteryChecker.args['sound']:
            try:
                playsound(os.path.join(BatteryChecker.BASE_DIR, "sounds", sound_file_name))
            except FileNotFoundError as e:
                print(f"Error: {e}")
            except PermissionError:
                print("Error: No tienes permisos para acceder al archivo.")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")
        

if __name__ == '__main__':
    BatteryChecker.parse_command_line()