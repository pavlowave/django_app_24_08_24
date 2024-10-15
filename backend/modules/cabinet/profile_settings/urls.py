from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path('settings/', ProfileAPIView.as_view(), name='settings'),
]