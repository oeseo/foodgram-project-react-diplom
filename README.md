# Проект - Фудграм

- Сайт: foodggram.hopto.org
- Логин: admin
- E-mail: admin@me.com
- Пароль: admin1234

## Описание проекта

Сервис для обмена рецептами!

## Стек технологий

- Python 3.9
- Django 3.2
- PostgreSQL
- Docker
- nodejs
- nginx
- gunicorn

## Запуск проекта на локале

Клонируйте репозиторий

```
https://github.com/oeseo/foodgram-project-react.git
```

В директории `infra` создайте файл `.env` и заполните

```
SECRET_KEY=ключ_Django_без_кавычек
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
DB_HOST=db
DB_PORT=5432
```

Из директории `infra` создайте и запустите контейнер

```
docker compose up -d --build
```

- После запуска проект будут доступен: http://localhost/
- Документация будет доступна: http://localhost/api/docs/
