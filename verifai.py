import instaloader
import os
import google.generativeai as generai
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Verifai:
    def __init__(self):
        self.L = instaloader.Instaloader(
            dirname_pattern='verifica_ai_temp',
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern=''
        )

        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        self.API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
        self.PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
        self.DEBUG = os.getenv("DEBUG")

        generai.configure(api_key=self.API_KEY_GEMINI)
        self.model = generai.GenerativeModel("gemini-1.5-flash")

        self.temp_path = "verifica_ai_temp"