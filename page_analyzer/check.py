import requests
import validators
from bs4 import BeautifulSoup


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