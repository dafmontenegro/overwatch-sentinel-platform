from flask import Flask

app = Flask(__name__)

@app.route("/")
def mensaje():
    return "Mensaje secreto desde EMISOR en 8080"