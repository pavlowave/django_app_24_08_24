from django.contrib.auth import get_user_model

def activate_user(strategy, details, user=None, *args, **kwargs):
    if user:
        user.is_active = True
        user.save()
