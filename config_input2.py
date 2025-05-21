import requests
import os
import instaloader
import time
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
from video_analyzer import VideoAnalyzer
from image_analyzer import ImageAnalyzer
from internet_analyzer import InternetAnalyzer

load_dotenv()

class ControlsInput(VideoAnalyzer, ImageAnalyzer, InternetAnalyzer):
    def __init__(self):
        super().__init__()

    def upload_file(self, filename):
        file = self.client.files.upload(file=filename)
        state = genai.types.FileState.PROCESSING
        while state == genai.types.FileState.PROCESSING:
            state = self.client.files.get(name=file.name).state
            time.sleep(1)
        return file
    def process_content(self, content):
        is_link_shared_reel = content.get("is_link_shared_reel", False)
        is_shared_reel = content.get("is_shared_reel", False)
        if is_link_shared_reel:
            response = requests.get(content["text"], allow_redirects=True)
            url = response.url
            content["shortcode"] = url.rstrip('/').split('/')[-1]
        try:
            shortcode = str(content["shortcode"])
            if is_shared_reel or content.get("type") == "video":
                response = requests.get(content["file_src"], stream=True)
                ext = 'mp4' if content.get("type") == "video" else 'jpg'
                filename = f"{self.temp_path}/v_{shortcode}.{ext}"
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return self.process_video(filename) if content.get("type") == "video" else self.process_image(filename)
            else:
                post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                self.L.download_post(post, target="verifica_ai_temp")
                time.sleep(10)
                filename = f"{self.username}_{shortcode}.{'mp4' if post.is_video else 'jpg'}"
                return self.process_video(filename) if post.is_video else self.process_image(filename)
        except Exception as e:
            print(e)
            traceback.print_exc()

    def send_message_to_user(self, instagram_account_id, user_id, message_text):
        url = f"https://graph.instagram.com/v22.0/me/messages"
        payload = {
            "messaging_product": "instagram",
            "recipient": {"id": user_id},
            "message": {"text": message_text}
        }
        headers = {"Authorization": f"Bearer {self.PAGE_ACCESS_TOKEN}"}
        requests.post(url, headers=headers, json=payload)


    def analyze(self, data):
        try:
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            if sender_id == '17841474389423643' or 'read' in messaging_event:
                return
                
            instagram_account_id = data['entry'][0]['id']
            if 'message' not in messaging_event:
                return
                
            message = messaging_event['message']
            content = {}
            prompt_content = []
            file = None

            if 'attachments' in message:
                # lógica de attachments permanece
                pass
            else:
                text = message.get('text', '')
                content['text'] = text
                user_question = text

            # Se for pergunta de texto, use a API de busca
            if 'text' in content:
                print(f"[DEBUG] Recebida pergunta: '{user_question}'")
                
                # Buscar informações via API
                scraped_text = self.web_search_api(user_question)
                print(f"[DEBUG] Texto retornado pela busca ({len(scraped_text)} caracteres)")
                
                # Verificar se a resposta indica um erro de API
                if scraped_text.startswith("Não foi possível realizar a pesquisa"):
                    # Gerar resposta de fallback sem dados de pesquisa
                    fallback_response = (
                        "Desculpe, não consegui verificar esta informação no momento devido a "
                        "um problema técnico. Por favor, tente novamente mais tarde ou "
                        "consulte fontes oficiais sobre este assunto."
                    )
                    self.send_message_to_user(instagram_account_id, sender_id, fallback_response)
                    print("[DEBUG] Enviada resposta de fallback devido a erro na API")
                    return
                    
                base_prompt = (
                    f"Analise a mensagem: \"{user_question}\"\n\n"
                    "É necessário responder se é fake news ou não? Se for necessário, diga se é (sim) ou não, ou Nenhuma análise (Use um emoji de ✅ ou ❌, ou ◽ ), "
                    "e classifique-a (dentro de parenteses) como: Clickbait, conteúdo enganoso, "
                    "fora de contexto, manipulado, etc. Depois diga os motivos. "
                    "Não utilize markdown na resposta. OBS: Responda com no máximo 1000 caracteres."
                    "Use as fontes de pesquisas para analisar a veracidade do fato."
                    "Se for apenas um prompt qualquer, sem necessidade de análise, retorne apenas a resposta. "
                )
                
                if scraped_text and not scraped_text.startswith("Não foi possível"):
                    full_prompt = base_prompt + "\n\nCONTEXTO DE PESQUISA PARA VERIFICAÇÃO:\n" + scraped_text
                else:
                    full_prompt = base_prompt
                    
                prompt_content = [full_prompt]
                print(f"[DEBUG] Prompt pronto, tamanho: {len(full_prompt)} caracteres")

            if not prompt_content:
                print("[DEBUG] Nenhum conteúdo para enviar ao modelo. Abortando análise.")
                return

            try:
                print(f"[DEBUG] Enviando prompt ao modelo, tamanho: {len(prompt_content[0])}")
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt_content,
                )

                answer = ''
                for part in response.candidates[0].content.parts:
                    answer += part.text

                chunks = getattr(response.candidates[0], 'groundingChunks', None)
                if chunks:
                    answer += "\nFontes:\n"
                    for fc in chunks:
                        answer += f"  {fc.web.title}: {fc.web.uri}\n"
                        
            except Exception as model_error:
                print(f"[DEBUG] Erro na geração de conteúdo: {str(model_error)}")
                answer = ("Desculpe, estou enfrentando dificuldades técnicas para processar "
                        "sua solicitação no momento. Por favor, tente novamente mais tarde.")

            print(f"[DEBUG] Enviando resposta ao usuário")
            self.send_message_to_user(instagram_account_id, sender_id, answer)
            print("[DEBUG] Resposta enviada com sucesso")

        except Exception as e:
            print(f"[DEBUG] ERRO na função analyze: {str(e)}")
            traceback.print_exc()
            # Tente enviar uma mensagem de erro para o usuário se possível
            try:
                error_message = "Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde."
                if 'instagram_account_id' in locals() and 'sender_id' in locals():
                    self.send_message_to_user(instagram_account_id, sender_id, error_message)
            except:
                print("[DEBUG] Não foi possível enviar mensagem de erro ao usuário")