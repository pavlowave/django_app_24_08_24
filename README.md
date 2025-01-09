

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
    SECRET_KEY=
    EMAIL_HOST = 
    EMAIL_PORT = 
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = 
    EMAIL_HOST_PASSWORD = 
    DEFAULT_FROM_EMAIL = 
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
