from rest_framework import serializers
from django.contrib.auth import get_user_model
import string
import secrets

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']  # Сохраняем только email

    def create(self, validated_data):
        email = validated_data['email']

        # Создайте пользователя с временным паролем
        user = User.objects.create_user(email=email, password=None)  # Пароль не устанавливается сразу
        user.is_active = False  # Пользователь неактивен до подтверждения
        user.save()
        return user
