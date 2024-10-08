

## __Установка на локальном компьютере__
1. Клонируйте репозиторий:
    ```
    git clone git@github.com:pavlowave/django_app_24_08_24
    ```
2. Установите и активируйте виртуальное окружение:

    ```
    cd backend
    python -m venv venv
    source venv/Scripts/activate  - для Windows
    source venv/bin/activate - для Linux
    ```
3. Установите зависимости:
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Создаем файл .env со следующим содержимым::
    ```
    DEBUG=True
    SECRET_KEY=h+8hy9&ye)gslawy0oij)kum=^4ko)enij42f)4ys@q+b+y_k1
    EMAIL_HOST = 'smtp.yandex.ru'
    EMAIL_PORT = 465
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = 'pavlowave@yandex.ru'
    EMAIL_HOST_PASSWORD = 'waufrybbzzghroly'
    DEFAULT_FROM_EMAIL = 'pavlowave@yandex.ru'
    ```


5.  Выполните миграции:
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Запустите проект:
    ```
    python manage.py runserver
    ```
