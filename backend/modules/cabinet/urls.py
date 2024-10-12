from django.urls import path
from .views import CabinetAPIView
from .views import LogoutView


urlpatterns = [
    path('cabinet/<int:user_id>/', CabinetAPIView.as_view(), name='cabinet'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
