import secrets
import string
import uuid
import time

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.translation import gettext_lazy as _
from core.models import Pan
from web.forms import PanConfirmDelete, RegisterForm

User = get_user_model()

class PanCreateView(CreateView):
    model = Pan
    fields = ["price", "vendor", "diameter"]

class PanUpdateView(UpdateView):
    model = Pan
    fields = ["price", "vendor"]
    template_name_suffix = '_update_form'

class PanDeleteView(DeleteView):
    model = Pan
    success_url = reverse_lazy('web:create_pan')
    form_class = PanConfirmDelete


@login_required
def profile_view(request):
    # Проверяем, является ли пользователь администратором
    if request.user.is_staff:
        # Перенаправляем администраторов на страницу входа
        return redirect(reverse('login'))

    # Отображаем страницу профиля для обычных пользователей
    return render(request, 'web/profile.html')

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy("web:profile")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        cache_key = f"email_sent_{email}"
        last_sent = cache.get(cache_key)

        # Получаем значение из настроек, по умолчанию 60 секунд
        email_cooldown = getattr(settings, 'EMAIL_SEND_COOLDOWN', 60)

        # Проверяем, прошло ли время, указанное в конфиге
        if last_sent and time.time() - last_sent < email_cooldown:
            form.add_error("email", _("You can only request an email once every minute."))
            return self.form_invalid(form)

        user, created = User.objects.get_or_create(email=email)
        new_pass = None

        if created:
            alphabet = string.ascii_letters + string.digits
            new_pass = ''.join(secrets.choice(alphabet) for i in range(8))
            user.set_password(new_pass)
            user.save(update_fields=["password", ])

        if new_pass or user.is_active is False:
            token = uuid.uuid4().hex
            redis_key = settings.DJANGO_APP_USER_CONFIRMATION_KEY.format(token=token)
            cache.set(redis_key, {"buyer_id": user.id}, timeout=settings.DJANGO_APP_USER_CONFIRMATION_TIMEOUT)

            confirm_link = self.request.build_absolute_uri(
                reverse_lazy(
                    "web:register_confirm", kwargs={"token": token}
                )
            )
            message = _(f"follow this link %s \n"
                        f"to confirm! \n" % confirm_link)
            if new_pass:
                message += f"Your new password: {new_pass} \n "

            send_mail(
                subject=_("Please confirm your registration!"),
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ]
            )

            # Устанавливаем время отправки
            cache.set(cache_key, time.time(), timeout=email_cooldown)

        return super().form_valid(form)


def register_confirm(request, token):
    redis_key = settings.DJANGO_APP_USER_CONFIRMATION_KEY.format(token=token)
    buyer_info = cache.get(redis_key) or {}

    if buyer_id := buyer_info.get("buyer_id"):
        buyer = get_object_or_404(User, id=buyer_id)
        buyer.is_active = True
        buyer.save(update_fields=["is_active"])
        return redirect(to=reverse_lazy("web:profile"))
    else:
        return redirect(to=reverse_lazy("web:register"))


def index(request):
    return render(request, 'web/index.html')


class WebPasswordResetView(PasswordResetView):
    template_name = 'web/password_reset_email.html'
