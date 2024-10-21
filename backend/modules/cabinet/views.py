from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .serializers import UserSerializer

User = get_user_model()

class CabinetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_list(self, user):
        """ Возвращает список пользователей в зависимости от роли текущего пользователя. """
        if user.is_superuser:
            return User.objects.all()
        elif user.role == 'manager':
            return User.objects.exclude(is_superuser=True).exclude(role='manager')
        elif user.role == 'admin':
            return User.objects.exclude(is_superuser=True).exclude(role__in=['manager', 'admin'])
        return User.objects.filter(id=user.id)

    def get_roles_to_assign(self, user):
        """ Возвращает роли, доступные для назначения в зависимости от роли текущего пользователя. """
        if user.role == 'admin':
            return ['visitor', 'trainer', 'masseur']
        elif user.role == 'manager':
            return ['visitor', 'trainer', 'masseur', 'admin']
        return []

    def get(self, request, *args, **kwargs):
        user = request.user
        users_list = self.get_user_list(user)
        roles_to_assign = self.get_roles_to_assign(user)

        # Пагинация
        page_number = request.GET.get('page', 1)
        paginator = Paginator(users_list, 25)

        try:
            users = paginator.page(page_number)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        # Сериализация данных пользователей
        user_data = UserSerializer(users, many=True).data

        # Ответ в формате JSON
        context = {
            'current_user': UserSerializer(user).data,  # Информация о текущем пользователе
            'users': user_data,  # Информация о всех пользователях (с учетом роли)
            'page': page_number,
            'roles_to_assign': roles_to_assign,
            'total_pages': paginator.num_pages,
        }
        return render(request, 'cabinet/cabinet.html', context)


    def post(self, request, *args, **kwargs):
        user = request.user
        new_role = request.data.get('role')
        target_user_email = request.data.get('email')

         # Проверка на наличие данных
        if not target_user_email or not new_role:
            return Response({'error': 'Email пользователя и новая роль обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        # Изменение роли для текущего пользователя
        if user.role in ['admin', 'manager']:
            try:
                target_user = User.objects.get(email=target_user_email)
            except User.DoesNotExist:
                return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

            # Проверка на допустимость новой роли
            valid_roles = self.get_roles_to_assign(user)  # Получаем доступные роли
            if new_role not in valid_roles:
                return Response({'error': f'Недопустимая роль. Доступные роли: {valid_roles}.'}, status=status.HTTP_400_BAD_REQUEST)

            # Изменение роли
            target_user.role = new_role
            target_user.save()
            return Response({'message': f'Роль пользователя {target_user.email} обновлена на {new_role}.'}, status=status.HTTP_200_OK)

        return Response({'error': 'У вас нет прав для изменения ролей.'}, status=status.HTTP_403_FORBIDDEN)


class LogoutView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
        return HttpResponseRedirect('/api/v1/login/')