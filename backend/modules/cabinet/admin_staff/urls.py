from django.urls import path
from .views import ScanUserAPIView

urlpatterns = [
    path('scan_user/', ScanUserAPIView.as_view(), name='scan_user'),
]
