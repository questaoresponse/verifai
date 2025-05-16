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

def get_media_content():
    url = f"https://graph.facebook.com/v19.0/instagram_oembed?url=https://www.instagram.com/p/Cxyz123/&access_token=690938390225465|860956c0ef8da5df7de45a25fe1756a2y"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        'User-Agent':'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)'
    }
    # samsung mobile user-agent
    content = requests.get(url, headers=headers).json() 
    print(content)
    # keys = list(content["data"]["user"].keys())
    # for i in range(len(keys)):
    #     print(keys[i],content["data"]["user"][keys[i]])
    # print(content["data"]["user"]["edge_owner_to_timeline_media"]["edges"])
get_media_content()
def analyze(data):
    try:
        messaging_event = data['entry'][0]['messaging'][0]
        sender_id = messaging_event['sender']['id']
        instagram_account_id = data['entry'][0]['id']
        text = messaging_event['message'].get('text')
        if text:
            if text.startswith("https://www.instagram.com/p/"):
                text = process_video(text)
            
            response = model.generate_content(text)
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