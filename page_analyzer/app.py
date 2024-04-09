from flask import (Flask,
                   request,
                   render_template,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages)
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from page_analyzer.db import (add_site_to_urls,
                              check_if_exist,
                              add_site_to_url_checks,
                              get_url_by_id,
                              get_checks_by_id,
                              get_url_by_name,
                              get_all_urls)
from page_analyzer.check import validate, parsing_url_data, normalize_url
import requests


load_dotenv()
SECRET = os.getenv('SECRET_KEY')


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route("/")
def index():
    return render_template(
        'index.html'
    )


@app.post('/urls')
def post_url():
    url = request.form.get('url')
    valid_error = validate(url)
    if valid_error:
        flash(valid_error, 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url,
            messages=messages), 422
    elif check_if_exist(url):
        flash('Страница уже существует', 'alert-success')
        id_ = get_url_by_name(normalize_url(url))['id']
        return redirect(url_for('urls_id', id_=id_))
    else:
        id_ = add_site_to_urls(url)
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('urls_id', id_=id_))


@app.route('/urls/<int:id_>')
def urls_id(id_):
    url = get_url_by_id(id_)
    if not url:
        return render_template('404.html')
    checks = get_checks_by_id(id_)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'show_url.html',
        url=url,
        checks=checks,
        messages=messages)


@app.get('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls/<int:id_>/checks')
def url_check(id_):
    url = get_url_by_id(id_)['name']
    if not url:
        return render_template('404.html')
    try:
        check = parsing_url_data(url)
        check['url_id'] = id_
        check['created_at'] = datetime.now().date().strftime("%Y-%m-%d")
        add_site_to_url_checks(check)
        flash('Страница успешно проверена', 'alert-success')

    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')

    return redirect(url_for('urls_id', id_=id_))


if __name__ == '__main__':
    app.run()
