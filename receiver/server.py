from flask import Flask, request, render_template
app = Flask("__main__")
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/receiver", methods=["POST"])
def receiver():
    with open("config_data.json", "w") as f:
        f.write(request.form["content"], f, indent=4)
    return "", 200
if __name__ == "__main__":
    app.run("0.0.0.0", 5000)