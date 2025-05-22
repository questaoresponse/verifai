from flask import Flask, request
import json
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host = os.getenv("MYSQL_HOST"),
    port = os.getenv("MYSQL_PORT"),
    user = os.getenv("MYSQL_USER"),
    password = os.getenv("MYSQL_PASSWORD"),
    database = "defaultdb",
    ssl_verify_cert = True,
    ssl_ca = "./ca.pem"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(100),
    type INT,
    expect INT,
    result INT
)
""")

app = Flask(__name__)

@app.route("/list", methods=["GET"])
def list():
    cursor.execute("SELECT * FROM links")
    return json.dumps({ "result": "true", "data": cursor.fetchall() }), 200

@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json()
    link = data["link"]
    tipo = data["type"]
    expect = data["expect"]
    cursor.execute("INSERT INTO links (id, link, type, expect, result) VALUES (%s, %s)", (id, link, tipo, expect, 2))
    conn.commit()
    return json.dumps({ "result": "true" }), 200

if __name__ == "__main__":
    app.run("0.0.0.0", 12345)