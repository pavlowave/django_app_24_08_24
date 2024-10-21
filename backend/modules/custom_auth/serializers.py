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
        fields = ['email', 'first_name', 'last_name', 'birth_date', 'phone', 'gender', 'club', 'photo']

    def validate_photo(self, value):
        if not value:
            raise serializers.ValidationError("Фото обязательно для регистрации.")
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        birth_date = validated_data.get('birth_date')
        phone = validated_data.get('phone')
        gender = validated_data.get('gender')
        club = validated_data.get('club')
        photo = validated_data.get('photo')

        # Создаем пользователя с неиспользуемым паролем (для последующей соц. аутентификации)
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            phone=phone,
            gender=gender,
            club=club,
            photo=photo,
            password=None  # Пароль не устанавливается, пока не будет подтвержден
        )
        user.is_active = False  # Пользователь не активен до подтверждения
        user.save()

        return user