# Evitar información sensible en el código
from dotenv import load_dotenv
import os

# Carga las variables de entorno del archivo .env
load_dotenv()

# Accede a las variables de entorno
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Ahora sí el código de mensajería Telegram
import requests

MESSAGE = "Este es un mensaje desde Python"

url = "https://api.telegram.org/bot" + str(TOKEN) + "/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    print("Mensaje enviado a Telegram con éxito.")
else:
    print("Error al enviar mensaje:", response.text)