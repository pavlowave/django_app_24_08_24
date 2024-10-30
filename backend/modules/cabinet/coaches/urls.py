from django.urls import path
from .views import CoachesAPIView, CoachDetailView

urlpatterns = [
    path('coaches/', CoachesAPIView.as_view(), name='coaches'),
    path('coaches/<int:user_id>/', CoachDetailView.as_view(), name='coach_detail'),  # Исправлено
]
