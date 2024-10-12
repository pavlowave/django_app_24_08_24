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
        user_email = user.email
        user_id = user.id

        # Получаем список пользователей и роли для назначения
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

        # Формируем контекст
        context = {
            'email': user_email,
            'roles_to_assign': roles_to_assign,
            'user_id': user_id,
            'user': user,
            'users': users,
            'paginator': paginator
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

        # Изменение роли
        target_user.role = new_role
        target_user.save()
        return Response({'message': f'Роль пользователя {target_user.email} обновлена на {new_role}.'}, status=status.HTTP_200_OK)



class LogoutView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            logout(request)
        return HttpResponseRedirect('/api/v1/login/')
