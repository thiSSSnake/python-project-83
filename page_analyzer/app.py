from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
import os
from dotenv import load_dotenv


load_dotenv()
SECRET = os.getenv('SECRET_KEY')


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET


@app.route("/")
def index():
    return render_template(
        'index.html'
    )