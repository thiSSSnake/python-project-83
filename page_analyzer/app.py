from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from urllib.parse import urlparse
import validators


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


def get_all_urls():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:

        query_s = '''SELECT DISTINCT ON (urls.id)
        urls.id AS id,
        urls.name AS name
        FROM urls
        ORDER BY urls.id DESC'''
        cur.execute(query_s)
        all_urls = cur.fetchall()
    conn.close()
    return all_urls


def get_url_by_name(name_url):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        query_s = 'SELECT * FROM urls WHERE name=(%s)'
        curs.execute(query_s, [name_url])
        urls = curs.fetchone()
    conn.close()
    return urls


def get_url_by_id(id_):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        query_s = '''SELECT * FROM urls WHERE id=(%s)'''
        curs.execute(query_s, [id_])
        urls = curs.fetchone()
    conn.close()
    return urls


@app.post('/urls')
def post_url():
    conn = psycopg2.connect(DATABASE_URL)
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
        with conn.cursor() as curs:
            query_s = '''INSERT INTO urls(name, created_at) VALUES(%s, %s)'''
            parsed_url = urlparse(url)
            normalize_url = '' + parsed_url.scheme + '://' + parsed_url.netloc
            site = {'url': normalize_url, 'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            curs.execute(query_s, (site['url'], site['created_at']))
            conn.commit()
        conn.close()
        id_ = get_url_by_name(normalize_url)['id']
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('urls_id', id_ = id_))


@app.route('/urls/<int:id_>')
def urls_id(id_):
    url = get_url_by_id(id_)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show_url.html', url=url, messages=messages)


@app.get('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)



if __name__ == '__main__':
    app.run(debug=True)