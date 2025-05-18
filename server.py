from controls_input import analyze

from flask import Flask
import requests
import os
import socketio
import threading

app = Flask(__name__)

io = socketio.Client()

@io.event
def connect():
    print("Conectado ao servidor.")

@io.event
def disconnect():
    print("Desconectado do servidor.")

#13c704a8b51257b55615159eeb5dc4e8



@io.event
def webhook(data):
    analyze(data)

@app.route("/", methods=["GET"])
def send_requests():
    try:
        requests.get("https://verifai.onrender.com")
    except Exception as e:
        print("error", e)
    threading.Timer(10, send_requests).start()  # executa a cada 2 segundos
    return None
#io.connect('https://verifai-proxy.onrender.com')
DEBUG = os.getenv("DEBUG") == "true"
if not DEBUG:
    send_requests()
io.connect("https://verifai-proxy-uxrm.onrender.com")
# io.connect("http://127.0.0.1:12345" if DEBUG else "https://verifai-proxy.onrender.com")