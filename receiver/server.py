from flask import Flask, render_template
app = Flask("__main__")
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/receiver", methods=["POST"])
def receiver():
    print(request.form["content"])
if __name__ == "__main__":
    app.run("0.0.0.0", 5000)