# Проект Foodgram

## Описание 

Проект Foodgram предназначен для воплощения ваших самых смелых кулинарных фантазий!

Собири из нескольких тысяч ингредиентов рецепты своей мечты!
Назначь им теги, а затем фильтруй рецепты по ним!
Подпишись на таких же красавчиков, как ты сам, и используй их рецепты!
Собири корзину из самых утонченных блюд и скачай в формате PDF все ингредиенты, необходимые для приготовления!

## Шаблон наполнения .env файла

DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY # секретный ключь Django проета из файла settings.py

## Команды для запуска приложения в контейнерах:

docker-compose up (-d) - разворачивает docker-compose проект

docker-compose stop - остановка контейнеров

winpty docker-compose exec backend python manage.py migrate

winpty docker-compose exec backend python manage.py createsuperuser

winpty docker-compose exec backend python manage.py collectstatic --no-input

## Команды для заполнения базы данными

sudo docker-compose exec web python manage.py load_data

### Над проектом работал:

- Денис Кудаков | [Github](https://github.com/DK0894)

### Статус workflow

![status workflow](https://github.com/DK0894/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Адрес сервера

1) http://51.250.106.249/api
2) http://51.250.106.249/admin
3) http://51.250.106.249/redoc

### Логин и пароль администратора

Login: admin@admin.admin
Password: 78493674n

### MIT License

Copyright (c) 2022 Denis Kudakov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.