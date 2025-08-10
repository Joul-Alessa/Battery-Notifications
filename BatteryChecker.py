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
    _instance = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start(self):
        # Carga las variables de entorno del archivo .env
        load_dotenv(os.path.join(self.BASE_DIR, ".env"))

        # Se accede a la información del json y se guardas su infomación
        try:
            with open(os.path.join(self.BASE_DIR, 'conf.json'), 'r') as file:
                self.args = json.load(file)
        except FileNotFoundError:
            print("Error: The file was not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            sys.exit(1)

        # Accede a las variables de entorno
        self.TOKEN = os.getenv("TOKEN")
        self.CHAT_ID = os.getenv("CHAT_ID")
        self.isrunning = True
    
    def restart(self):
        self.isrunning = False
        self.start()

    # Función que revisa cuando el archivo está por ser interrumpido (para las suspensiones y apagados)
    def stop(self):
        self.isrunning = False
        if self.args['closing']:
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
        while self.isrunning:
            try:
                pythoncom.PumpWaitingMessages()  
                battery = watcher(timeout_ms=1000)  # Espera evento

                if battery is None:
                    continue
                
                level = battery.EstimatedChargeRemaining
                status = battery.BatteryStatus  # 1 = descargando, 2 = cargando

                

                if level <= self.args['lower'] and status == 1:
                    messageNotif = f"⚠️ Nivel de batería bajo ({level} %). \nConecta el cargador."
                    self.send_notification("Alerta de Batería", messageNotif)
                    self.send_telegram_message(messageNotif)
                    self.play_notification_sound("battery-low.mp3")
                    time.sleep(self.args['sleepTime'])
                elif level >= self.args['higher'] and status == 2:
                    messageNotif = f"⚡ Batería casi llena ({level} %). \nConsidera desconectar el cargador."
                    self.send_notification("Alerta de Batería", messageNotif)
                    self.send_telegram_message(messageNotif)
                    self.play_notification_sound("battery-high.mp3")
                    time.sleep(self.args['sleepTime'])
            except pythoncom.com_error as e:
                print(f"Error COM: {e} - Reiniciando monitor WMI")
                self._restart_wmi_watcher()
            except Exception as e:
                print(f"Error inesperado: {e}")
                time.sleep(5)

    # Recuperación de errores WMI
    def _restart_wmi_watcher(self):
        pythoncom.CoInitialize()  # Reiniciar COM
        self.watcher = c.watch_for(notification_type="Modification", wmi_class="Win32_Battery")
    
    # Función que manda mansaje a través de Telegram
    def send_telegram_message(self,message):
        if self.args['msgTelegram']:
            url = "https://api.telegram.org/bot" + str(self.TOKEN) + "/sendMessage"
            payload = {
                "chat_id": self.CHAT_ID,
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
    def send_notification(self,title, message):
        #Señal a la GUI para disparar la notificación con su información correspondiente
        wenas=0

    # Función que reproduce el sonido para la notifiaciones de sistema en PC
    def play_notification_sound(self,sound_file_name):
        if self.args['sound']:
            try:
                playsound(os.path.join(self.BASE_DIR, "sounds", sound_file_name))
            except FileNotFoundError as e:
                print(f"Error: {e}")
            except PermissionError:
                print("Error: No tienes permisos para acceder al archivo.")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")
        

if __name__ == '__main__':
    BatteryChecker.parse_command_line()