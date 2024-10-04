from django.apps import AppConfig

class CustomAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.custom_auth'
    verbose_name = 'Аутентификация и Авторизация'
