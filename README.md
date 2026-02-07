FOODGRAM - это веб-приложение для публикации и обмена рецептами. Пользователи могут создавать рецепты, добавлять их в избранное, подписываться на авторов и формировать список покупок.

Ссылка на сайт: http://51.250.97.200

Функциональность сайта:
- Регистрация и авторизация пользователей
- Создание/редактирование/удаление рецептов с изображениями
- Тегирование рецептов (завтрак, обед, ужин)
- Список ингредиентов с возможностью поиска
- Добавление в избранное и список покупок
- Подписка на авторов рецептов
- Формирование списка покупок в формате PDF/TXT
- Фильтрация рецептов по тегам, автору, избранному

Стек технологий, использовавшихся при создании сайта:
    - Django
    - Gunicorn
    - Django REST Framework
    - Nginx
    - PostgreSQL
    - Python
    - JavaScript
    - React
    - Docker
    - Github Actions

Локальное развертывание:
    git clone https://github.com/ArOb-1/foodgram.git
    cd foodgram/infra

Сгенерируйте новый ключ командой:
    python -c "import secrets; print(secrets.token_urlsafe(50))"
Пример заполнения .env файла:
SECRET_KEY=*вставьте сюда сгенерированный ключ*
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,51.250.97.200
DB_NAME=foodgram
DB_USER=foodgram_user
DB_PASSWORD=ваш_пароль
DB_HOST=db
DB_PORT=5432

Сборка проекта.
    Находясь в папке infra выполните команды:
    docker compose up -d --build
    docker-compose exec backend python manage.py migrate
    docker compose exec backend python manage.py collectstatic
    docker-compose exec backend python manage.py createsuperuser
    docker-compose exec backend python manage.py loaddata ingredients.json

Описание проекта.
    Backend (Django REST Framework):
        - REST API для управления рецептами, пользователями, подписками
        - Аутентификация через JWT токены
        - Админ-панель Django для управления контентом
        - PostgreSQL для хранения данных
        - Nginx + Gunicorn для обслуживания запросов
    Frontend (React):
        - Одностраничное приложение (SPA)
        - Интерактивные формы создания/редактирования рецептов
        - Динамическая фильтрация и поиск
После того как вы выполните этап Сборки проекта система запустит 3 основных контейнера:
    backend — Django приложение на порту 8000
    db — PostgreSQL база данных на порту 5432
    frontend — React приложение, собранная статика

Примеры запросов:
    POST /api/users/
    Content-Type: application/json

    {
        "email": "user@example.com",
        "username": "newuser",
        "first_name": "Иван",
        "last_name": "Иванов",
        "password": "SecurePass123!"
    }
    POST /api/auth/jwt/create/
    Content-Type: application/json

    {
        "username": "newuser",
        "password": "SecurePass123!"
    }
    Получите в ответ:
    {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    Получение списка рецептов с фильтрацией:
    GET /api/recipes/?tags=breakfast&tags=lunch&author=2&is_favorited=1

Список использованных библиотек:
    Django==3.2.3
    djangorestframework==3.12.4
    djoser==2.1.0
    webcolors==1.11.1
    psycopg2-binary==2.9.3
    Pillow==9.0.0
    pytest==6.2.4
    pytest-django==4.4.0
    pytest-pythonpath==0.7.3
    PyYAML==6.0.1
    environs
    gunicorn==23.0.0
    django-filter==22.1
    djangorestframework-simplejwt==4.8.0
