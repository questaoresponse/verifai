from server import Server
from dotenv import load_dotenv

load_dotenv()

server = Server()

if __name__=="__main__":
    server.app.run("0.0.0.0", 5000)