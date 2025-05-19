import instaloader
import requests
import os
import time
import random
import glob
import PIL.Image as pil
from dotenv import load_dotenv
from verifai import Verifai

# Carrega variáveis de ambiente
load_dotenv()

class ImageAnalyzer(Verifai):
    def __init__(self):
        Verifai.__init__(self)

    # def download_image(self, url: str) -> list:
        # prompt = f"Faça uma análise da imagem {filename} acima e diga oque está escrito nela. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos. OBS: Responda com no máximo 1000 caracteres."
        # img = pil.open(filename)
        # """
        #     Faz o download das imagens de um post dado seu shortcode.
        #     Retorna a lista de caminhos locais dos arquivos de imagem baixados.
        # """
        # try:
        #     post = instaloader.Post.from_shortcode(self.L.context, shortcode)
        # except Exception as e:
        #     print(f"Erro ao obter o post: {e}")
        #     return []

        # if post.is_video:
        #     print("Erro: o post é um vídeo, não uma imagem.")
        #     return []

        # self.L.download_post(post, target=self.temp_path)

        # # Coleta arquivos de imagem baixados
        # downloaded = []
        # for ext in ['*.jpg', '*.jpeg', '*.png']:
        #     for fname in glob.glob(os.path.join(self.temp_path, f"{shortcode}_{ext}")):
        #         downloaded.append(fname)

        # if not downloaded:
        #     # em alguns casos, as imagens são nomeadas sem shortcode prefixo
        #     for ext in ['*.jpg', '*.jpeg', '*.png']:
        #         for fname in glob.glob(os.path.join(self.temp_path, ext)):
        #             downloaded.append(fname)

        # print(f"Total de imagens baixadas: {len(downloaded)}")
        # time.sleep(random.uniform(2, 5))  # delay aleatório
        # return downloaded

    # Função principal

    def process_image(self, filename: str) -> list:
        # """
        # Processa um URL de post do Instagram (https://www.instagram.com/p/<shortcode>/).
        # Retorna a lista de caminhos das imagens baixadas no post.
        # """
        # # Extrair shortcode da URL
        # #  url.rstrip('/').split('/')[-1]
   
        #                 response = self.model.generate_content([prompt,img])
        # shortcode = instaloader.Post.mediaid_to_shortcode(18075837601871193)
        img = pil.open(filename)
        return [ img, "image" ]
    