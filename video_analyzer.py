import instaloader
import os
import glob
import subprocess
import whisper
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

L = instaloader.Instaloader(dirname_pattern='verifica_ai_temp', download_video_thumbnails=False,
                                download_geotags=False, save_metadata=False, download_comments=False,
                                post_metadata_txt_pattern='')

username =  os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")


if os.path.isfile(f"session/{username}"):
    L.load_session_from_file(username, filename=f"session/{username}")  # se já tiver salvo antes
else:
    L.login(username, password)  # Vai fazer o login e manter a sessão
    L.save_session_to_file(filename=f"session/{username}")

# Baixar vídeo do Instagram
def video_download(url, content):
    is_shared_reel = content["is_shared_reel"]
    if is_shared_reel:
        response = requests.get(content.url, allow_redirects=True)
        url = response.url
        content["shortcode"] = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
    print(content["shortcode"])
    try:
        post = instaloader.Post(L.context,  instaloader.Post.mediaid_to_shortcode(L.context, content["shortcode"])) if is_shared_reel else instaloader.Post.from_mediaid(L.context, content["shortcode"])
        if post.is_video:
            print("Baixando vídeo...")
            L.download_post(post, target='verifica_ai_temp')
            time.sleep(random.uniform(5, 10))
            return True
        else:
            print("Erro: o post não é um vídeo.")
            return False
    except Exception as e:
        print("Erro ao tentar baixar o post:", str(e))
        return False

# Extrair áudio com ffmpeg (com tratamento de erro)
def extrair_audio():
    arquivos = glob.glob("verifica_ai_temp/*.mp4")
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo de vídeo .mp4 encontrado.")

    video_path = arquivos[0]
    print(video_path)
    audio_path = "verifica_ai_temp/audio.wav"

    print(f"Convertendo vídeo: {video_path}")

    comando = [
        'ffmpeg',
        '-y',
        '-i', video_path,
        '-vn',
        '-ar', '16000',
        '-ac', '1',
        '-f', 'wav',
        audio_path
    ]

    try:
        resultado = subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(video_path)
        return audio_path
    except subprocess.CalledProcessError as e:
        print("Erro na conversão com ffmpeg:")
        print(e.stderr.decode())
        os.remove(video_path)
        raise

# Transcrever com Whisper
def transcrever_audio(caminho_audio):
    print("Transcrevendo áudio com Whisper...")
    model = whisper.load_model("base")  # Pode usar 'small', 'medium' ou 'large' se quiser mais precisão
    result = model.transcribe(caminho_audio)
    return result["text"]

# Função principal
def process_video(url, is_object):
    print(f"Iniciando processamento do post: {url}\n")
    if video_download(url, is_object):
        try:
            audio = extrair_audio()
            texto = transcrever_audio(audio)
            return texto
        except Exception as erro:
            print(f"Falha ao processar o vídeo: {erro}")
    else:
        print("Não foi possível baixar ou identificar um vídeo no post.")