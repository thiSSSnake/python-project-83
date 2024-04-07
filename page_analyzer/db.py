import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_all_urls():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:

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


def get_checks_by_id(id_):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        query_s = '''SELECT * FROM url_checks
                        WHERE url_id=(%s) ORDER BY id DESC'''
        curs.execute(query_s, [id_])
        checks = curs.fetchall()
    conn.close()
    return checks


def normalize_url(url):
    parsed_url = urlparse(url)
    normalize_url = '' + parsed_url.scheme + '://' + parsed_url.netloc
    return normalize_url


def add_site_to_urls(url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
        query_s = '''INSERT INTO urls(name, created_at) VALUES(%s, %s)'''
        url = normalize_url(url)
        site = {
            'url': url,
            'created_at': datetime.now().date().strftime("%Y-%m-%d")
            }
        curs.execute(query_s, (site['url'], site['created_at']))
        conn.commit()
    conn.close()


def add_site_to_url_checks(check):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
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
        conn.commit()
    conn.close()
