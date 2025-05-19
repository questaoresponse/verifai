from server import Server
import os
import json
from dotenv import load_dotenv

load_dotenv()

config = None

server = Server()

with open("config_data.json") as f:
    config = json.load(f)

os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + config["ffmpeg_path"]

if __name__=="__main__":
    server.app.run("0.0.0.0", 5000)