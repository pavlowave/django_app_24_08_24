from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import render
from datetime import timedelta

User = get_user_model()


def admin_page(request):
    people_in_gym = User.objects.filter(in_gym=True).count()  # Счетчик людей в зале
    users = User.objects.all()
    context = {
        'people_in_gym': people_in_gym,
        'users': users,
    }
    return render(request, 'roles/admin.html', context)


class ScanUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        qr_code = request.data.get('qr_code')  # Получаем QR-код из запроса

        if not qr_code:
            return Response({"error": "QR-код не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=qr_code)  # Ищем по email, так как QR содержит email
            if not user.in_gym:  # Проверяем, не находится ли уже в зале
                user.in_gym = True
                user.entry_time = timezone.now()
                user.save()
                return Response({"message": f"Пользователь {user.email} запущен в зал."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Пользователь уже в зале."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)



def auto_logout_users():
    now = timezone.now()
    users_in_gym = User.objects.filter(in_gym=True)
    for user in users_in_gym:
        if now - user.entry_time > timedelta(minutes=90):
            user.in_gym = False
            user.save()