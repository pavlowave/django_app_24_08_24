from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

User = get_user_model()


class CoachesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_coach_list(self):
        """ Возвращает список всех тренеров. """
        return User.objects.filter(role='trainer')

    def get(self, request):
        coaches = self.get_coach_list()
        return render(request, 'cabinet/coaches.html', {'coaches': coaches})


class CoachDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        trainer = get_object_or_404(User, id=user_id)
        return render(request, 'cabinet/coach_detail.html', {'coach': trainer})