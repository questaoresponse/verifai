import instaloader
import os
import time
import random
import glob
from dotenv import load_dotenv
from verifai import Verifai

# Carrega variáveis de ambiente
load_dotenv()

class ImageAnalyzer(Verifai):
    def __init__(self):
        Verifai.__init__(self)

    def download_image(self, shortcode: str) -> list:
        """
            Faz o download das imagens de um post dado seu shortcode.
            Retorna a lista de caminhos locais dos arquivos de imagem baixados.
        """
        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
        except Exception as e:
            print(f"Erro ao obter o post: {e}")
            return []

        if post.is_video:
            print("Erro: o post é um vídeo, não uma imagem.")
            return []

        self.L.download_post(post, target=self.temp_path)

        # Coleta arquivos de imagem baixados
        downloaded = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            for fname in glob.glob(os.path.join(self.temp_path, f"{shortcode}_{ext}")):
                downloaded.append(fname)

        if not downloaded:
            # em alguns casos, as imagens são nomeadas sem shortcode prefixo
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                for fname in glob.glob(os.path.join(self.temp_path, ext)):
                    downloaded.append(fname)

        print(f"Total de imagens baixadas: {len(downloaded)}")
        time.sleep(random.uniform(2, 5))  # delay aleatório
        return downloaded

    # Função principal

    def process_image(self, content: str) -> list:
        """
        Processa um URL de post do Instagram (https://www.instagram.com/p/<shortcode>/).
        Retorna a lista de caminhos das imagens baixadas no post.
        """
        # Extrair shortcode da URL
        #  url.rstrip('/').split('/')[-1]
        shortcode = instaloader.Post.mediaid_to_shortcode(18075837601871193)
        return self.download_image(shortcode)