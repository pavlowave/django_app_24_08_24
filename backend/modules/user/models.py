from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('visitor', 'Посетитель'),
        ('trainer', 'Тренер'),
        ('masseur', 'Массажист'),
        ('admin', 'Админ'),
    )

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='visitor')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        permissions = [
            ("can_assign_trainer_role", "Can assign trainer role"),
            ("can_assign_masseur_role", "Can assign masseur role"),
        ]

    def __str__(self):
        return self.email