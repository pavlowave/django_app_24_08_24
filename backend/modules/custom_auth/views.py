import time
import string
import secrets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import LoginSerializer, RegistrationSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import PasswordResetView
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View


User = get_user_model()

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'registration/login.html')

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if request.user.is_authenticated:
            email = request.user.email
        else:
            email = None
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)  # Вход пользователя
            return redirect(reverse('cabinet') + f'?email={email}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CabinetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            email = request.user.email
        else:
            email = None
        return render(request, 'cabinet/cabinet.html', {'email': email})


class RegistrationAPIView(APIView):

    def get(self, request):
        return render(request, 'registration/registration.html', {'user': request.user})

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # Проверка существования пользователя с активным email
            if User.objects.filter(email=email, is_active=True).exists():
                return Response({'email': 'Данный Email уже используется.'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка на частоту отправки email
            cache_key = f"email_sent_{email}"
            last_sent = cache.get(cache_key)
            email_cooldown = getattr(settings, 'EMAIL_SEND_COOLDOWN', 60)

            if last_sent and time.time() - last_sent < email_cooldown:
                return Response({'email': 'Вы можете запрашивать электронное письмо только один раз в минуту.'},
                                status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()  # Создаем пользователя

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

    def get(self, request):
        email = request.GET.get('email')
        return render(request, 'registration/confirm_registration.html', {'email': email})

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(code):
            user.is_active = True
            user.save(update_fields=["is_active"])
            login(request, user)
            return redirect(reverse('cabinet'))

        return Response({'detail': 'Неверный код подтверждения.'}, status=status.HTTP_400_BAD_REQUEST)


class WebPasswordResetAPIView(PasswordResetView):
    template_name = 'reset_password/password_reset_email.html'



class LogoutView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # Завершаем сессию пользователя
            logout(request)
        # Перенаправляем пользователя на главную страницу или другую страницу после выхода
        return HttpResponseRedirect('/')