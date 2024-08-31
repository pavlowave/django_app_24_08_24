from django.urls import path
from .views import PanCreateView, PanUpdateView, PanDeleteView, profile_view, RegisterView, WebPasswordResetView, \
    register_confirm

app_name = 'web'

urlpatterns = [
    path('pans/', PanCreateView.as_view(), name='create_pan'),
    path('pans/<int:pk>/', PanUpdateView.as_view(), name='update_pan'),
    path('pans/<int:pk>/delete/', PanDeleteView.as_view(), name='delete_pan'),
    path('profile/', profile_view, name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password_reset/', WebPasswordResetView.as_view(), name='password_reset'),
    path('register/confirm/<str:token>/', register_confirm, name='register_confirm'),
]
