import os
import json
import whisper

config = None

with open("config_data.json") as f:
    config = json.load(f)

os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + config["ffmpeg_path"]

audio_filename = "verifica_ai_temp/v_18054194003002491.wav"
audio_filename = os.path.abspath(audio_filename)


model = whisper.load_model("base")  # Pode usar 'small', 'medium' ou 'large' se quiser mais precisão
result = model.transcribe(audio_filename)
os.remove(audio_filename)
print(result["text"])