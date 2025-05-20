import requests
import os
import instaloader
import time
import random
import traceback
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
from video_analyzer import VideoAnalyzer
from image_analyzer import ImageAnalyzer

load_dotenv()


class ControlsInput(VideoAnalyzer, ImageAnalyzer):
    def __init__(self):
        pass
    def upload_file(self, filename):
        file = self.client.files.upload(file = filename)

        state = genai.types.FileState.PROCESSING
        while state == genai.types.FileState.PROCESSING:
            state = self.client.files.get(name = file.name).state
            time.sleep(1)

        return file

    # Processa o conteudo do link e retorna o tipo do link e retorna o nome do arquivo baixado e o tipo dele
    def process_content(self, content):
        is_link_shared_reel = content["is_link_shared_reel"]
        is_shared_reel = content["is_shared_reel"]
        if is_link_shared_reel:
            response = requests.get(content["text"], allow_redirects=True)
            url = response.url
            content["shortcode"] = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
        try:  
            shortcode = str(content["shortcode"])
            if is_shared_reel or content["type"] == "video":
                response = requests.get(content["file_src"], stream=True)
                filename = None
                if content["type"] == "video":
                    filename = f"{self.temp_path}/v_{str(shortcode)}.mp4"
                else:
                    filename = f"{self.temp_path}/v_{str(shortcode)}.jpg"
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if content["type"] == "video":
                    return self.process_video(filename)
                else:
                    return self.process_image(filename)
            else:               
                post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                self.L.download_post(post, target="verifica_ai_temp")
                time.sleep(10)
                filename = ""
                if post.is_video:
                    filename = f"{self.username}_{shortcode}.mp4"
                    return self.process_video(filename)
                else:
                    filename = f"{self.username}_{shortcode}.jpg"
                    return self.process_image(filename)

        except Exception as e:
            print(e)
            traceback.print_exc()
    # def get_next_image_filename():
    #     i = 1
    #     while os.path.exists(f"imagem_recebida_{i}.jpg"):
    #         i += 1
    #     return f"imagem_recebida_{i}.jpg"

    def send_message_to_user(self, instagram_account_id, user_id, message_text):
        url = f"https://graph.instagram.com/v22.0/me/messages"
        payload = {
            "messaging_product": "instagram",
            "recipient": {"id": user_id},
            "message": {"text": message_text}
        }
        headers = {
            "Authorization": f"Bearer {self.PAGE_ACCESS_TOKEN}"
        }
        requests.post(url, headers=headers, json=payload).json()

    def analyze(self, data):
        try:
            print(data)
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            if sender_id == '17841474389423643' or "read" in messaging_event:
                return
            instagram_account_id = data['entry'][0]['id']
            if not ("message" in messaging_event):
                return
            message = messaging_event["message"]
            content = {}
            prompt_content = []
            file = None
            filename = None
            if "attachments" in message:
                if message["attachments"][0]["type"]=="ig_reel":
                    content = { "type": "video", "shortcode": int(message["attachments"][0]["payload"]["reel_video_id"]), "file_src": message["attachments"][0]["payload"]["url"], "caption": message["attachments"][0]["payload"]["title"], "is_media": True, "is_shared_reel": True, "is_link_shared_reel": False  }
                elif message["attachments"][0]["type"]=="video":
                    content = { "type": "video", "shortcode": message["attachments"][0]["payload"]["url"].split("=")[1].split("&")[0], "file_src": message["attachments"][0]["payload"]["url"], "caption": "", "is_media": True, "is_shared_reel": False, "is_link_shared_reel": False  }
                else:
                    content = { "type": "image", "shortcode": message["attachments"][0]["payload"]["url"].split("=")[1].split("&")[0], "file_src": message["attachments"][0]["payload"]["url"], "caption": "", "is_media": True, "is_shared_reel": True, "is_link_shared_reel": False  }
            else:
                content["text"] = messaging_event['message'].get('text')
                if content["text"].startswith("https://www.instagram.com/share/"):
                    content["is_reel"] = True
                    content["is_link_shared_reel"] = True
                    content["is_shared_reel"] = False
                elif content["text"].startswith("https://www.instagram.com/p/") or content["text"].startswith("https://www.instagram.com/reel/"):
                    content["is_reel"] = True
                    content["is_link_shared_reel"] = False
                    content["is_shared_reel"] = False
                    content["shortcode"] = content["text"].split("/")[-2] if content["text"].endswith("/") else content["text"].split("/")[-1]
            if "is_media" in content:
                caption = content["caption"] if "caption" in content else ""
                content_data, content_type = self.process_content(content)

                file = self.upload_file(content_data)
                filename = content_data

                if content_type == "video":
                    prompt_content=[
                        f"Legenda: \"{caption}\". Faça a análise do conteúdo desse vídeo, tanto informações visuais (analizando a veracidade dos conteúdos mostrados) quanto audio, também a legenda fornecida. Primeiramente, me diga: 'É fake news' ou 'Não é fake news'. Depois diga os motivos, podendo realizar uma pesquisa sobre o assunto. OBS: Responda com no máximo 1000 (mil) caracteres.",
                        file
                    ]

                else:
                    prompt_content=[
                        f"Faça a análise detalhadamente do conteúdo presente nessa imagem. Primeiramente, me diga: 'É fake news' ou 'Não é fake news'. Depois diga os motivos, podendo realizar uma pesquisa sobre o assunto. OBS: Responda com no máximo 1000 caracteres.",
                        file
                    ]

            else:
                text = content["text"]
                prompt_content = [f"\"{text}\".Faça a análise desse texto. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos, podendo realizar uma pesquisa sobre o assunto. OBS: Responda com no máximo 1000 caracteres."]
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents = prompt_content,
                config = GenerateContentConfig(
                    tools = [self.google_search_tool],
                    response_modalities = ["TEXT"],
                )
            )

            if file:
                self.client.files.delete(name = file.name)
                os.remove(filename)
            
            for part in response.candidates[0].content.parts:
                text += part.text
            
            if "groundingChunks" in response.candidates[0] and len(response.candidates[0].groundingChunks) > 0:
                text += "\nFontes:\n"
                for font in response.candidates[0].groundingChunks:
                    text+=f"  {font.web.title}: {font.web.uri}\n"

            self.send_message_to_user(instagram_account_id, sender_id, text)
        except Exception as e:
            print(e)
            traceback.print_exc()