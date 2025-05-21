
import os
import platform
import zipfile
import tarfile
import requests
from pathlib import Path
import json

config_data = {}

if os.path.exists("config_data.json"):
    print("Ambiente já configurado.")
    exit(0)

def baixar_ffmpeg(destino_dir):
    sistema = platform.system().lower()
    destino_dir = Path(destino_dir)
    destino_dir.mkdir(parents=True, exist_ok=True)

    if sistema == "windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = destino_dir / "ffmpeg.zip"
    elif sistema == "linux":
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        zip_path = destino_dir / "ffmpeg.tar.xz"
    else:
        raise RuntimeError(f"SO não suportado: {sistema}")
    print("Baixando arquivo...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

    print("Extraindo FFmpeg...")
    if sistema == "windows":
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino_dir)
    elif sistema == "linux":
        with tarfile.open(zip_path, "r:xz") as tar_ref:
            tar_ref.extractall(destino_dir)

    ffmpeg_path = None
    for root, _, files in os.walk(destino_dir):
        for file in files:
            if file == "ffmpeg" or file == "ffmpeg.exe":
                ffmpeg_path = os.path.join(root, file)
                break

    os.remove(zip_path)

    if not ffmpeg_path:
        raise RuntimeError("FFmpeg não encontrado após extração.")
    
    print(f"FFmpeg baixado em: {ffmpeg_path}")
    return ffmpeg_path

Path(os.getcwd() + "/libs/ffmpeg").mkdir(exist_ok=True)
ffmpeg_path = baixar_ffmpeg("libs/ffmpeg")
config_data["ffmpeg_path"] = os.path.basename(ffmpeg_path)   

with open("config_data.json", "w") as f:
    f.write(json.dump(config_data, f, indent=4))