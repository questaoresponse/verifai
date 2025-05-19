import requests
import os
import PIL.Image as pil
from dotenv import load_dotenv
from video_analyzer import VideoAnalyzer
from image_analyzer import ImageAnalyzer

load_dotenv()

class ControlsInput(VideoAnalyzer, ImageAnalyzer):
    def __init__(self):
        pass

    def get_next_image_filename():
        i = 1
        while os.path.exists(f"imagem_recebida_{i}.jpg"):
            i += 1
        return f"imagem_recebida_{i}.jpg"

    def send_message_to_user(self, instagram_account_id, user_id, message_text):
        print(instagram_account_id)
        url = f"https://graph.instagram.com/v22.0/me/messages"
        payload = {
            "messaging_product": "instagram",
            "recipient": {"id": user_id},
            "message": {"text": message_text}
        }
        headers = {
            "Authorization": f"Bearer {self.PAGE_ACCESS_TOKEN}"
        }
        response = requests.post(url, headers=headers, json=payload).json()
        print(response)

    def analyze(self, data):
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
                if message["attachments"][0]["type"]=="ig_reel":
                    content = { "type": "video", "shortcode": int(message["attachments"][0]["payload"]["reel_video_id"]), "video_src": message["attachments"][0]["payload"]["url"], "caption": message["attachments"][0]["payload"]["title"], "is_reel": True, "is_shared_reel": True, "is_link_shared_reel": False  }
                else:
                    content = { "type": "image", "shortcode": message["attachments"][0]["payload"]["url"].split("=")[1].split("&")[0], "video_src": message["attachments"][0]["payload"]["url"], "caption": "", "is_reel": True, "is_shared_reel": True, "is_link_shared_reel": False  }
            else:
                content["text"] = messaging_event['message'].get('text')
                if content["text"].startswith("https://wwww.instagram.com/share/"):
                    content["is_reel"] = True
                    content["is_link_shared_reel"] = True
                elif content["text"].startswith("https://www.instagram.com/p/"):
                    content["is_reel"] = True
                    content["shortcode"] = content["text"].split("/")[-2] if content["text"].endswith("/") else content["text"].split("/")[-1] 
            if content:
                prompt = ""
                if "is_reel" in content:
                    caption = content["caption"] if "caption" in content else ""
                    content_proccessed = self.process_video(content) if content["type"] == "video" else self.process_image(content) 
                    prompt = f"Texto: \"{content_proccessed}\". Legenda: \"{caption}\". Faça a análise desses textos. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos. OBS: Responda com no máximo 1000 caracteres."
                else:
                    text = content["text"]
                    prompt = f"\"{text}\". Faça a análise desse texto. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos. OBS: Responda com no máximo 1000 caracteres."

                response = self.model.generate_content(prompt)
                self.send_message_to_user(instagram_account_id, sender_id, response.text)
                return
        except Exception as e:
            print("Não foi possível extrair o texto ou enviar resposta:", e)
        try:
            attachments = data['entry'][0]['messaging'][0]['message'].get('attachments', [])
            for att in attachments:
                if att['type'] == 'image':
                    image_url = att['payload'].get('url')
                    if image_url:
                        filename = self.get_next_image_filename()
                        img_data = requests.get(image_url).content
                        with open(filename, "wb") as handler:
                            handler.write(img_data)
                        prompt = f"Faça uma análise da imagem {filename} acima e diga oque está escrito nela. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos. OBS: Responda com no máximo 1000 caracteres."
                        img = pil.open(filename)
                        response = self.model.generate_content([prompt,img])
                        self.send_message_to_user(instagram_account_id, sender_id, response.text)
                    else:
                        print("Não foi possível obter a URL da imagem.")
        except Exception as e:
            print("Não foi possível salvar a imagem:", e)