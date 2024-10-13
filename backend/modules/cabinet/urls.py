from django.urls import path
from .views import CabinetAPIView, LogoutView


urlpatterns = [
    path('cabinet/', CabinetAPIView.as_view(), name='cabinet'),
    path('logout/', LogoutView.as_view(), name='logout'),
]