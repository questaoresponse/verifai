import instaloader
import os
import time
import random
import requests
import subprocess
import PIL.Image as pil
from faster_whisper import WhisperModel
from verifai import Verifai

class VideoAnalyzer(Verifai):
    def __init__(self):
        Verifai.__init__(self)
        pass
    
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
    def process_video(self, filename):
        try:
            return [ filename, "video" ]

            audio = self.extrair_audio(filename)
            texto = self.transcrever_audio(audio)
            return [ texto, "video" ]
        except Exception as erro:
            print(f"Falha ao processar o vídeo: {erro}")