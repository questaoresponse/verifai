import requests
import os
import instaloader
import time
import traceback
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
from video_analyzer import VideoAnalyzer
from image_analyzer import ImageAnalyzer
from internet_analyzer import InternetAnalyzer

load_dotenv()


class ControlsInput(VideoAnalyzer, ImageAnalyzer, InternetAnalyzer):
    def __init__(self):
        pass


    def upload_file(self, filename):
        file = self.client.files.upload(file = filename)

        state = genai.types.FileState.PROCESSING
        while state == genai.types.FileState.PROCESSING:
            state = self.client.files.get(name = file.name).state
            time.sleep(1)

        return file
    
    def get_text_from_prompt(self, response):
        if "candidates" in response:
            text = ""
            for part in response.candidates[0].content.parts:
                text += part.text
            return text
        
        return response.text

    def get_shortcode_from_url(self, url):
        url = url.split("?")[0]
        return url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]

    # Processa o conteudo do link e retorna o tipo do link e retorna o nome do arquivo baixado e o tipo dele
    def process_content(self, content):
        is_shared_reel = content["is_shared_reel"]

        try:  
            shortcode = content["shortcode"]
            if is_shared_reel or ("type" in content and content["type"] == "video"):
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
                self.L.download_post(content["post"], target="verifica_ai_temp")

                if content["post"].is_video:
                    filename = f"{self.temp_path}/vl_{shortcode}.mp4"
                    return self.process_video(filename)
                else:
                    filename = f"{self.temp_path}/vl_{shortcode}.jpg"
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

    def generate_response(self, prompt, use_google_search = False):
        if use_google_search:
            return self.get_text_from_prompt(
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                        config=GenerateContentConfig(
                        tools=[self.google_search_tool],
                        response_modalities=["TEXT"],
                    )
                )
            )

        return self.get_text_from_prompt(self.client.models.generate_content(
                model=self.model,
                contents=prompt
        ))

    # Retorna a resposta processada da GEMINI API, com base no tipo de conteúdo
    def get_response_from_type(self, type, content):
        is_media = type == "video" or type == "image"

        file = None

        if is_media:
            filename = content["filename"]
            file = self.upload_file(filename)
            os.remove(filename)

        if type == "video":
            caption = content["caption"]

            response_text = self.generate_response([
                f"Legenda: \"{caption}\". Analise o video detalhadamente e sua legenda. Para verificar se é fake news ou não, me diga exatamente separado por linhas, os temas que precisam ser pesquisados, sem gerar dados temporais com base em seus conhecimentos desatualizados. OBS: Não diga mais nada além do que pedi",
                file
            ])

            response_text = self.generate_response([
                f"""Legenda: \"{caption}\". Com base no video e na legenda apresentada, pesquise detalhadamente os seguintes assuntos: "{response_text}". Adapte os resultados ao contexto da mensagem, principalmente em relação ao tempo (atualidade), buscando sempre os mais recentes. Se for uma afirmação temporal, tente pequisar sobre ela em si.
                """,
                file
            ], True)

            response_text = self.generate_response([
                f"Legenda: \"{caption}\". Analise o video detalhadamente e a legenda, depois analise a veracidade deles com os seguintes resultados de pesquisa: \"{response_text}\". Agora, diga '✅ É fato' ou '❌ É fake' no começo da resposta, depois os motivos. Diga se não é fake news apenas se todos os dados condizerem com as pesquisas. OBS: Responda com menos de 1000 caracteres.",
                file
            ])

            self.client.files.delete(name = file.name)

            return response_text
    
        elif type == "image":
            response_text = self.generate_response([
                f"Transforme o conteúdo dessa imagem para uma pesquisa da web com o intuito de verificar a veracidade. Me diga exatamente separado por linhas, os temas que precisam ser pesquisados, sem gerar dados temporais com base em seus conhecimentos desatualizados. OBS: Não diga mais nada além do que pedi.",
                file
            ])

            response_text = self.generate_response([
                f"""Com base no conteúdo da imagem, pesquise detalhadamente os seguintes assuntos: "{response_text}". Adapte os resultados ao contexto da imagem, principalmente em relação ao tempo (atualidade), buscando sempre os mais recentes. OBS: Responda com menos de 1000 caracteres.
                """,
                file
            ], True)

            response_text = self.generate_response([
                f"Analise detalhadamente o conteúdo presente na imagem. Analise a veracidade da imagem com os seguintes resultados de pesquisa: \"{response_text}\". Agora, diga ''✅ É fato' ou '❌ É fake' no começo da resposta, depois os motivos. Diga se não é fake news apenas se todos os dados condizerem com as pesquisas. OBS: Responda com menos de 1000 caracteres",
                file
            ])

            self.client.files.delete(name = file.name)

            return response_text
    
        elif type == "text":
            text = content["text"]

            response_text = self.generate_response([
                f"Analise a mensagem: \"{text}\"\n. Para verificar se é fake news ou não, me diga exatamente separado por linhas, os temas que precisam ser pesquisados, sem gerar dados temporais com base em seus conhecimentos desatualizados. OBS: Não diga mais nada além do que pedi"
            ])
            
            response_text = self.generate_response((
                f"""Com base na mensagem: "{text}", pesquise detalhadamente os seguintes assuntos: "{response_text}". Adapte os resultados ao contexto da mensagem, principalmente em relação ao tempo (atualidade), buscando sempre os mais recentes. Se for uma afirmação temporal, tente pequisar sobre ela em si."""
            ), True)

            response_text = self.generate_response((
                f"Analise a mensagem \"{text}\". Analise a veracidade da mensagem com os seguintes resultados de pesquisa: \"{response_text}\". Agora, diga '✅ É fato' ou '❌ É fake' no começo da resposta, depois os motivos. Diga se não é fake news apenas se todos os dados condizerem com as pesquisas. OBS: Responda com menos de 1000 caracteres"
            ))
            
            return response_text

    # Extrai as principais informações recebidas do webhook da Graph API
    def process_webhook_message(self, data):
        messaging_event = data['entry'][0]['messaging'][0]
        sender_id = messaging_event['sender']['id']
        if sender_id == '17841474389423643' or "read" in messaging_event:
            return None
        instagram_account_id = data['entry'][0]['id']
        if not ("message" in messaging_event):
            return None
        message = messaging_event["message"]
        text = message["text"] if "text" in message else ""

        self.process_input(sender_id, instagram_account_id, message, text)
        
    # def analyze(self, sender_id, instagram_account_id, message, text):
    #     self.process_
    def get_content_object(self, message, text):
        content = None

        if "attachments" in message:
            if message["attachments"][0]["type"] == "ig_reel":
                content = { 
                    "type": "video",
                    "shortcode": int(message["attachments"][0]["payload"]["reel_video_id"]),
                    "file_src": message["attachments"][0]["payload"]["url"],
                    "caption": message["attachments"][0]["payload"]["title"] if "title" in message["attachments"][0]["payload"] else "",
                    "is_media": True,
                    "is_shared_reel": True,
                    "is_link_shared_reel": False
                }

            elif message["attachments"][0]["type"] == "video":
                content = { 
                    "type": "video",
                    "shortcode": message["attachments"][0]["payload"]["url"].split("=")[1].split("&")[0],
                    "file_src": message["attachments"][0]["payload"]["url"],
                    "caption": "",
                    "is_media": True,
                    "is_shared_reel": False,
                    "is_link_shared_reel": False
                }
            else:
                content = {
                    "type": "image",
                    "shortcode": message["attachments"][0]["payload"]["url"].split("=")[1].split("&")[0],
                    "file_src": message["attachments"][0]["payload"]["url"],
                    "caption": "",
                    "is_media": True,
                    "is_shared_reel": True,
                    "is_link_shared_reel": False
                }

        else:
            if text.startswith("https://www.instagram.com/share/"):
                response = requests.get(text, allow_redirects=True)
                url = response.url
                shortcode = self.get_shortcode_from_url(url)
                post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                caption = post.caption if post.caption else ""
                content = {
                    "is_media": True,
                    "is_link_shared_reel": True,
                    "is_shared_reel": False,
                    "shortcode": shortcode,
                    "post": post,
                    "caption": caption
                }


            elif text.startswith("https://www.instagram.com/p/") or text.startswith("https://www.instagram.com/reel/"):
                shortcode = self.get_shortcode_from_url(text)
                post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                caption = post.caption if post.caption else ""
                content = {
                    "is_media": True,
                    "is_link_shared_reel": False,
                    "is_shared_reel": False,
                    "shortcode": shortcode,
                    "post": post,
                    "caption": caption
                }

            else:
                content = { "text": text }

        return content
    
    def process_input(self, sender_id, instagram_account_id, message, text):
        self.send_message_to_user(instagram_account_id, sender_id, "Estamos analisando o conteúdo. Pode demorar alguns segundos...")
        content = self.get_content_object(message, text)
        response_text = self.process_post(content)
        self.send_message_to_user(instagram_account_id, sender_id, response_text)

    def process_post(self, content):
        try:
            
            if "is_media" in content:

                filename, type = self.process_content(content)
                
                new_content = {
                    "caption": content["caption"],
                    "filename": filename
                }
                return self.get_response_from_type(type, new_content)

            else:
                new_content = { 
                    "text": content["text"]
                }
                return self.get_response_from_type("text", new_content)
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents = prompt_content1,
                config = GenerateContentConfig(
                    tools = [self.google_search_tool],
                    response_modalities = ["TEXT"],
                )
            )


            if file:
                self.client.files.delete(name = file.name)
                os.remove(filename)
            
            text = ""
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