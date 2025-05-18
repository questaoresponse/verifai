from video_analyzer import process_video

import google.generativeai as generai
import requests
import os
import PIL.Image as pil
from dotenv import load_dotenv

load_dotenv()


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
    print(instagram_account_id)
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

def analyze(data):
    try:
        print(data)
        messaging_event = data['entry'][0]['messaging'][0]
        sender_id = messaging_event['sender']['id']
        if sender_id == '17841474389423643' or "read" in messaging_event:
            return
        instagram_account_id = data['entry'][0]['id']
        message = messaging_event["message"]
        content = {}
        if "attachments" in message:
            content = { "shortcode": int(message["attachments"][0]["payload"]["reel_video_id"]), "video_src": message["attachments"][0]["payload"]["url"], "caption": message["attachments"][0]["payload"]["title"], "is_reel": True, "is_shared_reel": True, "is_link_shared_reel": False  }
        else:
            content["text"] = messaging_event['message'].get('text')
            if content["text"].startswith("https://wwww.instagram.com/share/"):
                content["is_reel"] = True
                content["is_link_shared_reel"] = True
            elif content["text"].startswith("https://www.instagram.com/p/"):
                content["is_reel"] = True
                content["shortcode"] = content["text"].split("/")[-2] if content["text"].endswith("/") else content["text"].split("/")[-1] 
        if content:
            prompt = process_video(content, content) if "is_reel" in content else content["text"]
            response = model.generate_content(prompt)
            send_message_to_user(instagram_account_id, sender_id, response.text)
            return
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