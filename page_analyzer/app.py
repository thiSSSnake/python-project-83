from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"