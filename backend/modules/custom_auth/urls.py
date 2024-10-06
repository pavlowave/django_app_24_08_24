from django.urls import include, path
from modules.custom_auth.views import RegistrationAPIView, ConfirmRegistrationAPIView
from .views import CabinetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name='registration'),
    path('registration/confirm/', ConfirmRegistrationAPIView.as_view(), name='registration-confirm'),
    path('cabinet/', CabinetView.as_view(), name='cabinet'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
