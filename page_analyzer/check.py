import requests
import validators
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse


DATABASE_URL = os.getenv('DATABASE_URL')


def validate(url):
    if len(url) == 0:
        return 'Некорректный URL'
    elif len(url) > 255:
        return 'URL превышает 255 символов'
    elif not validators.url(url):
        return 'Некорректный URL'


def get_url_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    if requests.Response.raise_for_status(r):
        raise requests.RequestException

    url_data = {'status_code': r.status_code}

    description = soup.find('meta', attrs={'name': 'description'})
    description_tag = description['content']

    url_data['description_tag'] = description_tag
    url_data['title_tag'] = soup.find('title')
    url_data['h1_tag'] = soup.find('h1')
    return url_data


def parsing_url_data(url):
    url_data = get_url_data(url)

    check = {'status_code': url_data['status_code']}

    check['description'] = url_data['description_tag'].strip() \
        if url_data['description_tag'] else ''
    check['title'] = url_data['title_tag'].text.strip() \
        if url_data['title_tag'] else ''
    check['h1'] = url_data['h1_tag'].text.strip() \
        if url_data['h1_tag'] else ''
    return check


def normalize_url(url):
    parsed_url = urlparse(url)
    normalize_url = '' + parsed_url.scheme + '://' + parsed_url.netloc
    return normalize_url
