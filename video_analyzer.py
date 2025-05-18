import instaloader
import os
import glob
import whisper
import time
import random
import requests
from moviepy import VideoFileClip

temp_path = "verifica_ai_temp"

# Fazer login no Instaloader
L = instaloader.Instaloader(dirname_pattern=temp_path, download_video_thumbnails=False,
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
            filename = f"{temp_path}/v_{str(shortcode)}.mp4"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
        
        post = instaloader.Post.from_shortcode(L.context, content["shortcode"]) if "is_shared_reel" in content else instaloader.Post.from_shortcode(L.context, content["shortcode"])
        if post.is_video:
            print("Baixando vídeo...")
            L.download_post(post, target=temp_path)
            time.sleep(random.uniform(5, 10))
            filename = f"{username}_{shortcode}.mp4"
            return filename
        else:
            print("Erro: o post não é um vídeo.")
            return False
    except Exception as e:
        print("Erro ao tentar baixar o post:", str(e))
        return False

# Extrair áudio com moviepy
def extrair_audio(video_filename):
    audio_path = ".".join(video_filename.split(".")[:-1]) + ".wav"

    try:
        video = VideoFileClip(video_filename)
        video.audio.write_audiofile(audio_path, fps=16000, nbytes=2, buffersize=2000, codec='pcm_s16le')
        video.close()
        os.remove(video_filename)
        return audio_path
    except Exception as e:
        print("❌ Erro ao extrair áudio:", e)
        
# Transcrever com Whisper
def transcrever_audio(audio_filename):
    model = whisper.load_model("base")  # Pode usar 'small', 'medium' ou 'large' se quiser mais precisão
    result = model.transcribe(os.path.abspath(audio_filename))
    os.remove(audio_filename)
    return result["text"]

# Função principal
def process_video(url, is_object):
    print(f"Iniciando processamento do post: {url}\n")
    filename = video_download(url, is_object)
    if filename:
        try:
            audio = extrair_audio(filename)
            texto = transcrever_audio(audio)
            return texto
        except Exception as erro:
            print(f"Falha ao processar o vídeo: {erro}")
    else:
        print("Não foi possível baixar ou identificar um vídeo no post.")