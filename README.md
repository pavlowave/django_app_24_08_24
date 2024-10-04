

## __Установка на локальном компьютере__
1. Клонируйте репозиторий:
    ```
    git clone git@github.com:sxwiix/django_app_24_08_24
    ```
2. Установите и активируйте виртуальное окружение:
    ```
    python -m venv venv
    source venv/Scripts/activate  - для Windows
    source venv/bin/activate - для Linux
    ```
3. Установите зависимости:
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
4. Перейдите в папку django_app и выполните миграции:
    ```
    cd django_app
    python manage.py migrate
    ```

5. Запустите проект:
    ```
    python manage.py runserver или python manage.py runserver 8080 если на ngrok
    ```
6. Зайти на локал хосте по адресу и выполнить тест или на ngrok:
    ```
    http://127.0.0.1:8000/accounts/login/
    ```
Пароль создается при вводе имейла и если человек 
логинится первый раз на почту приходит пароль.
