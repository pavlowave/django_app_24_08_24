from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View


User = get_user_model()


class CabinetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        email = request.user.email if request.user.is_authenticated else None
        is_admin = request.user.role == 'admin'  # Проверка на роль админа

        return render(request, 'cabinet/cabinet.html', {'email': email, 'is_admin': is_admin})


class AssignRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()  # Получите всех пользователей
        return render(request, 'cabinet/assign_role.html', {'users': users})

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        try:
            user = User.objects.get(id=user_id)
            user.role = role
            user.save()
            return redirect('cabinet')  # Вернуться на главную страницу кабинета
        except User.DoesNotExist:
            # Обработка ошибки, если пользователь не найден
            return render(request, 'cabinet/assign_role.html', {'error': 'Пользователь не найден'})

class ViewUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()  # Получите всех пользователей
        return render(request, 'cabinet/view_users.html', {'users': users})


class LogoutView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
        return HttpResponseRedirect('/api/v1/login/')