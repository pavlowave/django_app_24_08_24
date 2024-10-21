from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import qrcode
from io import BytesIO
from django.core.files import File
import os


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('visitor', 'Посетитель'),
        ('trainer', 'Тренер'),
        ('masseur', 'Массажист'),
        ('admin', 'Администратор'),
        ('manager', 'Управляющий'),
    )

    GENDERS = (
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    )

    CLUBS = (
        ('club1', 'Клуб 1'),
        ('club2', 'Клуб 2'),
    )

    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDERS)
    club = models.CharField(max_length=50, choices=CLUBS)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='visitor')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'birth_date', 'gender', 'club', 'photo']


    def generate_qr_code(self):
        """Генерация QR-кода для пользователя на основе email."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.email)
        qr.make(fit=True)

        # Сохранение изображения в памяти
        img = qr.make_image(fill='black', back_color='white')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Удаление старого QR-кода (если он был)
        if self.qr_code:
            if os.path.isfile(self.qr_code.path):
                os.remove(self.qr_code.path)

        # Сохранение нового QR-кода
        self.qr_code.save(f'qr_code_{self.id}.png', File(img_io), save=False)

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения для генерации QR-кода."""
        # Сначала сохраняем пользователя (если он новый, то у него еще нет ID)
        if not self.pk:
            super().save(*args, **kwargs)

        # Генерируем и сохраняем QR-код
        self.generate_qr_code()

        # Сохраняем пользователя с уже сохранённым QR-кодом
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email
