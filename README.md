### Hexlet tests and linter status:
[![Actions Status](https://github.com/thiSSSnake/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/thiSSSnake/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/b26234a57b64ba400c5a/maintainability)](https://codeclimate.com/github/thiSSSnake/python-project-83/maintainability)
## О приложении
Page Analyzer – это сайт, который анализирует указанные страницы на SEO-пригодность по аналогии с PageSpeed Insights:
![](docs/images/1.jpg)
![](docs/images/2.jpg)
![](docs/images/3.jpg)

## Деплой приложения
Зависимости приложения:
- _python = "^3.10"_
- _flask = "^3.0.2"_
- _python-dotenv = "^1.0.1"_
- _gunicorn = "^21.2.0"_
- _jinja2 = "^3.1.3"_
- _psycopg2-binary = "^2.9.9"_
- _validators = "^0.28.0"_
- _requests = "^2.31.0"_
- _beautifulsoup4 = "^4.12.3"_

Так же приложение использует PostgreSQL
Структуру таблиц БД можно посмотреть в файле database.sql
# Установка
## How to install

```bash
git clone git@github.com:thiSSSnake/python-project-83.git
cd python-project-83/
# install poetry
make install
```

### Live Domen
[Live domen](https://python-project-83-swmd.onrender.com)