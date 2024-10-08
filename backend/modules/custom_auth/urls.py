from django.urls import path
from .views import LoginAPIView, RegistrationAPIView, ConfirmRegistrationAPIView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('registration/', RegistrationAPIView.as_view(), name='registration'),
    path('registration/confirm/', ConfirmRegistrationAPIView.as_view(), name='registration-confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
