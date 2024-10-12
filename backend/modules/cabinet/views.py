from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

User = get_user_model()


class CabinetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_email = request.user.email
        user_id = request.user.id
        user = request.user
        roles_to_assign = []

        # Логика для получения списка пользователей
        if user.is_superuser:
            users_list = User.objects.all()  # Суперадминистратор видит всех в админке
        elif user.role == 'manager':
            users_list = User.objects.exclude(is_superuser=True).exclude(role='manager')  # Менеджер видит всех, кроме суперадминистраторов
        elif user.role == 'admin':
            users_list = User.objects.exclude(is_superuser=True).exclude(role__in=['manager', 'admin'])  # Админ видит всех, кроме суперадминистраторов и менеджеров

        else:
            users_list = User.objects.filter(id=user_id)  # Остальные видят только себя

        # Пагинация
        page = request.GET.get('page', 1)  # Получаем номер страницы из GET-запроса
        paginator = Paginator(users_list, 25)  # 25 пользователей на странице

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)  # Если не целое число, возвращаем первую страницу
        except EmptyPage:
            users = paginator.page(paginator.num_pages)  # Если страница больше последней, возвращаем последнюю

        # Проверка роли и добавление доступных для назначения ролей
        if user.role == 'admin':
            roles_to_assign = ['visitor', 'trainer', 'masseur']
        elif user.role == 'manager':
            roles_to_assign = ['visitor', 'trainer', 'masseur', 'admin']

        # Объединение всех данных в один контекст
        context = {
            'email': user_email,
            'roles_to_assign': roles_to_assign,
            'user_id': user_id,
            'user': user,
            'users': users,  # Список пользователей для отображения на странице
            'paginator': paginator  # Передаем пагинатор для создания навигации
        }
        return render(request, 'cabinet/cabinet.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        target_user_id = request.data.get('user_id')
        new_role = request.data.get('role')

        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        # Изменение роли целевого пользователя
        target_user.role = new_role
        target_user.save()
        return Response({'message': f'Роль пользователя {target_user.email} обновлена на {new_role}.'}, status=status.HTTP_200_OK)


class LogoutView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
        return HttpResponseRedirect('/api/v1/login/')
