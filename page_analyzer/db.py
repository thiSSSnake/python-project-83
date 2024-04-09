import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from page_analyzer.check import normalize_url


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def initial_curs_dict_empty(func):
    def wrapper():
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as curs:
                return func(curs)
        finally:
            conn.commit()
            conn.close()
    return wrapper


def initial_curs_dict(func):
    def wrapper(*args):
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as curs:
                return func(curs, *args)
        finally:
            conn.commit()
            conn.close()
    return wrapper


def initial_curs(func):
    def wrapper(*args):
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor() as curs:
                return func(curs, *args)
        finally:
            conn.commit()
            conn.close()
    return wrapper


@initial_curs_dict_empty
def get_all_urls(curs):
    query_s = '''SELECT DISTINCT ON (urls.id)
                    urls.id AS id,
                    urls.name AS name,
                    url_checks.created_at AS last_check,
                    url_checks.status_code AS status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                AND url_checks.id = (SELECT MAX(id)
                                    FROM url_checks
                                    WHERE url_id = urls.id)
                ORDER BY urls.id DESC;'''
    curs.execute(query_s)
    all_urls = curs.fetchall()
    return all_urls


@initial_curs_dict
def get_url_by_name(curs, name_url):
    name_url = name_url
    query_s = 'SELECT * FROM urls WHERE name=(%s)'
    curs.execute(query_s, [name_url])
    urls = curs.fetchone()
    return urls


@initial_curs_dict
def get_url_by_id(curs, id_):
    id_ = id_
    query_s = '''SELECT * FROM urls WHERE id=(%s)'''
    curs.execute(query_s, [id_])
    urls = curs.fetchone()
    return urls


@initial_curs_dict
def get_checks_by_id(curs, id_):
    id_ = id_
    query_s = '''SELECT * FROM url_checks
                    WHERE url_id=(%s) ORDER BY id DESC'''
    curs.execute(query_s, [id_])
    checks = curs.fetchall()
    return checks


@initial_curs
def add_site_to_urls(curs, url):
    url = url
    query_s = '''INSERT INTO urls(name, created_at) VALUES(%s, %s)
                    RETURNING id;'''
    url = normalize_url(url)
    site = {
        'url': url,
        'created_at': datetime.now().date().strftime("%Y-%m-%d")
    }
    curs.execute(query_s, (site['url'], site['created_at']))
    id_ = curs.fetchone()[0]
    return id_


@initial_curs
def add_site_to_url_checks(curs, check):

    check = check
    query_s = '''INSERT INTO url_checks(
                    url_id,
                    created_at,
                    status_code,
                    h1,
                    description,
                    title)
                    VALUES(%s, %s, %s, %s, %s, %s)'''
    curs.execute(query_s, (
        check['url_id'],
        check['created_at'],
        check['status_code'],
        check['h1'],
        check['description'],
        check['title']))


@initial_curs_dict
def check_if_exist(curs, url):
    url = url
    norm_url = normalize_url(url)
    query_s = '''SELECT * FROM urls WHERE name=(%s)'''
    curs.execute(query_s, [norm_url])
    existing_site = curs.fetchone()
    return existing_site
