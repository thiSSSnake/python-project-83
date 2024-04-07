import requests
import validators
import psycopg2
import os
from bs4 import BeautifulSoup
from psycopg2.extras import RealDictCursor
from page_analyzer.db import normalize_url


DATABASE_URL = os.getenv('DATABASE_URL')


def check_if_exist(url):
    conn = psycopg2.connect(DATABASE_URL)
    norm_url = normalize_url(url)
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        query_s = '''SELECT * FROM urls WHERE name=(%s)'''
        curs.execute(query_s, [norm_url])
        existing_site = curs.fetchone()
    conn.close()
    return existing_site


def validate(url):
    error = None
    if check_if_exist(url):
        error = 'exist'

    if len(url) == 0:
        error = 'zero'

    elif len(url) > 255:
        error = 'length'
    
    elif not validators.url(url):
        error = 'invalid'

    validation = {'url': url, 'error': error}
    return validation


def get_url_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    if r.status_code != 200:
        raise requests.Response.raise_for_status()

    check = {'status_code': r.status_code}

    for meta in soup.find_all('meta', {'name': 'description'}):
        tag_content = meta.attrs['content'][:255]
        if tag_content:
            if len(tag_content) > 255:
                tag_content += '...'
        else:
            check['description'] = ''
        check['description'] = tag_content

    h1_tag = soup.find('h1')
    if h1_tag:
        h1_content = h1_tag.text
        check['h1'] = h1_content
    else:
        check['h1'] = ''

    if soup.title:
        check['title'] = soup.title.string
    else:
        check['title'] = ''

    return check