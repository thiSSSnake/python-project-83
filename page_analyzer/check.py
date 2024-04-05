import requests


def get_url_data(url):
    r = requests.get(url)

    if r.status_code != 200:
        raise requests.Response.raise_for_status()

    check = {'status_code': r.status_code}
    return check