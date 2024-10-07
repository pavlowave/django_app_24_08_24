from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Аутентификация пользователя
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Неверный email или пароль.")

        # Проверка, что пользователь активен
        if not user.is_active:
            raise serializers.ValidationError("Этот аккаунт деактивирован.")

        # Сохраняем аутентифицированного пользователя
        data['user'] = user
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def create(self, validated_data):
        email = validated_data['email']

        # Создаем пользователя с временным паролем
        user = User.objects.create_user(email=email, password=None)  # Пароль не устанавливается сразу
        user.is_active = False  # Пользователь неактивен до подтверждения
        user.save()
        return user