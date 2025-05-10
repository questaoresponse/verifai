from flask import Flask, request
import google.generativeai as generai
import requests
import os
import socketio
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

io = socketio.Client()

@io.event
def connect():
    print("Conectado ao servidor.")

@io.event
def disconnect():
    print("Desconectado do servidor.")

#13c704a8b51257b55615159eeb5dc4e8

API_KEY_GEMINAI = os.getenv("API_KEY_GEMINI")

generai.configure(api_key=API_KEY_GEMINAI)
model = generai.GenerativeModel("gemini-1.5-flash")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

url = f"https://graph.instagram.com/v22.0/me/messages"
payload = {
    "messaging_product": "instagram",
    "recipient": {"id": "1786410258631394"},
    "message": {"text": "eita cara"}
}
headers = {
    "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())

def get_next_image_filename():
    i = 1
    while os.path.exists(f"imagem_recebida_{i}.jpg"):
        i += 1
    return f"imagem_recebida_{i}.jpg"

def send_message_to_user(instagram_account_id, user_id, message_text):
    url = f"https://graph.instagram.com/v22.0/me/messages"
    payload = {
        "messaging_product": "instagram",
        "recipient": {"id": user_id},
        "message": {"text": message_text}
    }
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Resposta enviada ao usuário:", response.status_code, response.text)

@io.event
def webhook(data):
    try:
        data = json.loads(data)
        print("Recebido POST do webhook:")
        try:
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            instagram_account_id = data['entry'][0]['id']
            text = messaging_event['message'].get('text')
            if text:
                print("Texto recebido na DM:", text)
                response = model.generate_content(text)
                print("Resposta do Gemini:", response.text)
                # Envia a resposta para o usuário no Instagram
                send_message_to_user(instagram_account_id, sender_id, response.text)
        except Exception as e:
            print("Não foi possível extrair o texto ou enviar resposta:", e)
        try:
            attachments = data['entry'][0]['messaging'][0]['message'].get('attachments', [])
            for att in attachments:
                if att['type'] == 'image':
                    image_url = att['payload'].get('url')
                    if image_url:
                        filename = get_next_image_filename()
                        img_data = requests.get(image_url).content
                        with open(filename, "wb") as handler:
                            handler.write(img_data)
                        print(f"Imagem salva como {filename}")
                    else:
                        print("Não foi possível obter a URL da imagem.")
        except Exception as e:
            print("Não foi possível salvar a imagem:", e)
    except json.JSONDecodeError:
        print("Erro ao decodificar a resposta do servidor.")

io.connect('https://verifai-proxy.onrender.com')
io.wait()