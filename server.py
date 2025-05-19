from flask import Flask
import requests
import os
import socketio
import threading
from verifai import Verifai
from controls_input import ControlsInput

class Server(ControlsInput):
    def __init__(self):
        Verifai.__init__(self)
        ControlsInput.__init__(self)

        if os.path.isfile(f"{os.getcwd()}/session/{self.username}"):
            self.L.load_session_from_file(self.username, filename=f"{os.getcwd()}/session/{self.username}")  # se já tiver salvo antes
        else:
            self.L.login(self.username, self.password)  # Vai fazer o login e manter a sessão
            self.L.save_session_to_file(filename=f"{os.getcwd()}/session/{self.username}")

        self.app = Flask(__name__)

        self.io = socketio.Client()

        self.register_routes()

        self.io.connect("https://verifai-proxy-uxrm.onrender.com")

        DEBUG = self.DEBUG == "true"
        if not DEBUG:
            self.send_requests()

    def connect(self):
        print("Conectado ao servidor.")

    def disconnect(self):
        print("Desconectado do servidor.")

    def register_routes(self):
        self.io.on("connect", self.connect)
        self.io.on("disconnect", self.disconnect)
        self.io.on("webhook", self.webhook)

    #13c704a8b51257b55615159eeb5dc4e8

    def webhook(self, data):
        self.analyze(data)

    def send_requests(self):
        try:
            requests.get("https://verifai.onrender.com")
        except Exception as e:
            print("error", e)
        threading.Timer(10, self.send_requests).start()  # executa a cada 2 segundos
        return None
        #io.connect('https://verifai-proxy.onrender.com')
    # io.connect("http://127.0.0.1:12345" if DEBUG else "https://verifai-proxy.onrender.com")