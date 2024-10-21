import time
import string
import secrets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, RegistrationSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, get_backends, logout
from django.contrib.auth.views import PasswordResetView
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View


User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'registration/login.html')

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        # Проверка валидности данных
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Вход пользователя
            login(request, user)

            # Получение ID пользователя после успешного входа
            user_id = user.id

            # Редирект на личный кабинет с передачей ID пользователя в URL
            return redirect(reverse('cabinet'))

        # Если данные невалидны, возвращаем ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'registration/registration.html', {'user': request.user})

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            birth_date = serializer.validated_data['birth_date']
            phone = serializer.validated_data['phone']
            gender = serializer.validated_data['gender']
            club = serializer.validated_data['club']
            photo = serializer.validated_data['photo']


            # Проверка существования пользователя с активным email
            if User.objects.filter(email=email).exists():
                return Response({'email': 'Данный Email уже используется.'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка на частоту отправки email
            cache_key = f"email_sent_{email}"
            last_sent = cache.get(cache_key)
            email_cooldown = getattr(settings, 'EMAIL_SEND_COOLDOWN', 60)

            if last_sent and time.time() - last_sent < email_cooldown:
                return Response({'email': 'Вы можете запрашивать электронное письмо только один раз в минуту.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Создаем временного пользователя
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                phone=phone,
                gender=gender,
                club=club,
                photo=photo,
                is_active=False  # Устанавливаем is_active в False до подтверждения
            )
            user.set_password(None)  # Пароль пока не устанавливаем
            user.save()  # Сохраняем временного пользователя в БД

            # Генерируем код подтверждения
            digits = string.digits
            new_code = ''.join(secrets.choice(digits) for _ in range(6))
            user.set_password(new_code)  # Устанавливаем временный пароль
            user.save()

            # Отправляем письмо
            message = f"Ваш код подтверждения: {new_code}"
            send_mail(
                subject='Пожалуйста, подтвердите свою регистрацию!',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            cache.set(cache_key, time.time(), timeout=email_cooldown)  # Устанавливаем кэш на отправку email

            return redirect(reverse('registration-confirm') + f'?email={email}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.GET.get('email')
        return render(request, 'registration/confirm_registration.html', {'email': email})

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)  # Получаем пользователя
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(code):
            user.is_active = True
            user.save(update_fields=["is_active"])
            # Получаем первый бекенд аутентификации
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            # Входим в систему с указанием бекенда
            login(request, user, backend=user.backend)

            return redirect(reverse('cabinet'))

        return Response({'detail': 'Неверный код подтверждения.'}, status=status.HTTP_400_BAD_REQUEST)


class WebPasswordResetAPIView(PasswordResetView):
    template_name = 'reset_password/password_reset_email.html'