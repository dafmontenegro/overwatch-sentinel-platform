from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def intermedio():
    try:
        respuesta = requests.get("http://emisor:8080/")
        return f"Intermediario accedió a: {respuesta.text}"
    except Exception as e:
        return f"Error al conectar con emisor: {str(e)}"
