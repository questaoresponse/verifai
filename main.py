from flask import Flask, request
import google.generativeai as generai
import requests
import os
import socketio
import json
import threading, time
import PIL.Image as pil
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

API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")

generai.configure(api_key=API_KEY_GEMINI)
model = generai.GenerativeModel("gemini-1.5-flash")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

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
    requests.post(url, headers=headers, json=payload)

@io.event
def webhook(data):
    try:
        messaging_event = data['entry'][0]['messaging'][0]
        sender_id = messaging_event['sender']['id']
        instagram_account_id = data['entry'][0]['id']
        text = messaging_event['message'].get('text')
        if text:
            response = model.generate_content(text)
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
                    prompt = f"Faça uma análise da imagem {filename} acima e diga oque está escrito nela. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos."
                    img = pil.open(filename)
                    response = model.generate_content([prompt,img])
                    send_message_to_user(instagram_account_id, sender_id, response.text)
                else:
                    print("Não foi possível obter a URL da imagem.")
    except Exception as e:
        print("Não foi possível salvar a imagem:", e)

@app.route("/", methods=["GET"])
def send_requests():
    try:
        requests.get("https://verifai.onrender.com")
    except Exception as e:
        print("error", e)
    threading.Timer(10, send_requests).start()  # executa a cada 2 segundos
    return None
#io.connect('https://verifai-proxy.onrender.com')
DEBUG = os.getenv("DEBUG") == "true"
if not DEBUG:
    send_requests()
io.connect("http://127.0.0.1:12345" if DEBUG else "https://verifai-proxy.onrender.com")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)