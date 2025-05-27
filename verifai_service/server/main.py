from flask import Flask, request
import json
import pymysql
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

timeout = 10
conn = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host=os.getenv("MYSQL_HOST"),
  password=os.getenv("MYSQL_PASSWORD"),
  read_timeout=timeout,
  port=int(os.getenv("MYSQL_PORT")),
  user=os.getenv("MYSQL_USER"),
  write_timeout=timeout,
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
CORS(app)

@app.route("/list", methods=["GET"])
def list():
    cursor.execute("SELECT * FROM links")
    rows = cursor.fetchall()
    print(rows)
    return json.dumps({ "result": "true", "data": rows }), 200

@app.route("/insert", methods=["POST"])
def insert():
    try: 
        data = request.get_json()
        link = data["link"]
        tipo = int(data["type"])
        expect = int(data["expect"])
        cursor.execute("INSERT INTO links (link, type, expect, result) VALUES (%s, %s, %s, %s)", (link, tipo, expect, 2))
        conn.commit()
        return json.dumps({ "result": "true" }), 200
    except Exception as e:
        print(e)
        return json.dumps({ "result": "false" }), 200

@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json()
    id = int(data["id"])
    cursor.execute("DELETE FROM links WHERE id = %s", (id))
    cursor.commit()
    return list()

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    id_start = data["id_start"]
    id_end = data["id_end"]
    cursor.execute("SELECT * FROM links WHERE id > %s AND id < %s", (id_start, id_end))
    rows = cursor.fetchall()

    headers = {
        "VERIFY_TOKEN": os.getenv("VERIFY_TOKEN")
    }

    results = {}

    for row in rows:
        response = requests.post("http://127.0.0.1:5000", headers=headers).json()
        verify_result = 0 if "não" in response["data"][:10] else 1
        results[str(row["id"])] = verify_result

        cursor.execute("UPDATE links SET result = %s WHERE id = %s", (int(row["id"]), verify_result))
        cursor.commit()

    return json.dumps({ "result": "true", "results": results }), 200

if __name__ == "__main__":
    app.run("0.0.0.0", 12345)

# https://verifai-8z3i.onrender.com