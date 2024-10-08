from django.urls import path
from .views import AssignRoleView, CabinetAPIView, ViewUsersView
from .views import LogoutView


urlpatterns = [
    path('cabinet/', CabinetAPIView.as_view(), name='cabinet'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('assign-role/', AssignRoleView.as_view(), name='assign_role'),
    path('view-users/', ViewUsersView.as_view(), name='view_users'),
]
