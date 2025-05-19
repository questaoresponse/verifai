import instaloader
import os
import time
import random
import requests
import subprocess
from faster_whisper import WhisperModel
from verifai import Verifai

class VideoAnalyzer(Verifai):
    def __init__(self):
        Verifai.__init__(self)
        pass

    def video_download(self, content):
        is_link_shared_reel = content["is_link_shared_reel"]
        is_shared_reel = content["is_shared_reel"]
        if is_link_shared_reel:
            response = requests.get(content.url, allow_redirects=True)
            url = response.url
            content["shortcode"] = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
        try:
            shortcode = str(content["shortcode"])
            if is_shared_reel:
                response = requests.get(content["video_src"], stream=True)
                filename = f"{self.temp_path}/v_{str(shortcode)}.mp4"
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return filename
            
            post = instaloader.Post.from_shortcode(self.L.context, content["shortcode"]) if "is_shared_reel" in content else instaloader.Post.from_shortcode(L.context, content["shortcode"])
            if post.is_video:
                print("Baixando vídeo...")
                self.L.download_post(post, target=self.temp_path)
                time.sleep(random.uniform(5, 10))
                filename = f"{self.username}_{shortcode}.mp4"
                return filename
            else:
                print("Erro: o post não é um vídeo.")
                return False
        except Exception as e:
            print("Erro ao tentar baixar o post:", str(e))
            return False
    
    def extrair_audio(self, video_filename):
        audio_path = ".".join(video_filename.split(".")[:-1]) + ".wav"

        comando = [
            'ffmpeg',
            '-y',
            '-i', video_filename,
            '-vn',
            '-ar', '16000',
            '-ac', '1',
            '-f', 'wav',
            audio_path
        ]

        try:
            subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.remove(video_filename)
            return audio_path
        except subprocess.CalledProcessError as e:
            print("Erro na conversão com ffmpeg:")
            print(e.stderr.decode())
            os.remove(video_filename)
            raise
    
    def transcrever_audio(self, audio_filename):
        # Carregar o modelo (pode ser 'tiny', 'base', 'small', 'medium', 'large')
        model = WhisperModel("base", device="auto", compute_type="int8")  # use "int8" para mais leve

        # Transcrever o áudio
        segments, _ = model.transcribe(audio_filename, beam_size=5)  # pode ser .wav, .mp3, etc.

        os.remove(audio_filename)

        # Mostrar o texto transcrito
        # print("Idioma detectado:", info.language)
        text = ""
        for segment in segments:
            text+=segment.text

        return text

    # Função principal
    def process_video(self, content):
        filename = self.video_download(content)
        if filename:
            try:
                audio = self.extrair_audio(filename)
                texto = self.transcrever_audio(audio)
                return texto
            except Exception as erro:
                print(f"Falha ao processar o vídeo: {erro}")
        else:
            print("Não foi possível baixar ou identificar um vídeo no post.")