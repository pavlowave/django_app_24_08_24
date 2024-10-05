from django.urls import include, path
from modules.custom_auth.views import RegistrationView


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
     path('registration/', RegistrationView.as_view(), name='registration'),
]