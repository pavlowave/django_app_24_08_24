import time
import string
import secrets
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model, login
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView


User = get_user_model()


class CabinetView(TemplateView):
    template_name = 'cabinet/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.user.email
        return context


class RegistrationAPIView(APIView):

    def get(self, request):
        # Возвращаем HTML-шаблон с формой регистрации
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
