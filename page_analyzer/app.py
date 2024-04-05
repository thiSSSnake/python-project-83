from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import validators
from page_analyzer.db import add_site_to_urls, normalize_url, add_site_to_url_checks, get_url_by_id, get_checks_by_id, get_url_by_name, get_all_urls
from page_analyzer.check import get_url_data
import requests


load_dotenv()
SECRET = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET


@app.route("/")
def index():
    return render_template(
        'index.html'
    )


def validate(url):
    error = None

    if len(url) == 0:
        error = 'zero'

    elif len(url) > 255:
        error = 'length'
    
    elif not validators.url(url):
        error = 'invalid'

    validation = {'url': url, 'error': error}
    return validation


@app.post('/urls')
def post_url():
    url = request.form.get('url')
    valid = validate(url)
    error = valid['error']
    if error:
        if error == 'invalid':
            flash('Некорректный URL', 'alert-danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template('index.html', url=url, messages=messages), 422
        else:

            if error == 'zero':
                flash('URL обязателен', 'alert-danger')
            elif error == 'length':
                flash('URL превышает 255 символов', 'alert-danger')

            messages = get_flashed_messages(with_categories=True)
            return render_template(
                    'index.html',
                    url=url,
                    messages=messages
                ), 422
    else:
        add_site_to_urls(url)
        id_ = get_url_by_name(normalize_url(url))['id']
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('urls_id', id_ = id_))


@app.route('/urls/<int:id_>')
def urls_id(id_):
    url = get_url_by_id(id_)
    checks = get_checks_by_id(id_)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show_url.html', url=url, checks=checks, messages=messages)


@app.get('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls/<int:id_>/checks')
def url_check(id_):
    url = get_url_by_id(id_)['name']
    try:
        check = get_url_data(url)
        check['url_id'] = id_
        check['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_site_to_url_checks(check)

        flash('Страница успешно проверена', 'alert-success')

    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')

    return redirect(url_for('urls_id', id_ = id_))


if __name__ == '__main__':
    app.run(debug=True)