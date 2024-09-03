# В вашем файле, например, social_auth_pipeline.py
from django.contrib.auth import get_user_model

def activate_user(strategy, details, user=None, *args, **kwargs):
    if user:
        user.is_active = True
        user.save()
#сделать отслеживание был ли логин или нет