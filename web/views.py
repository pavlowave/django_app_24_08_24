import secrets
import string
import time
from django.contrib.auth import login as auth_login
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
        # Проверка наличия email в базе данных
        user_exists = User.objects.filter(email=email, is_active=True).exists()
        if user_exists:
            form.add_error("email", _("This email is already in use."))
            return self.form_invalid(form)
        cache_key = f"email_sent_{email}"
        last_sent = cache.get(cache_key)

        # Получаем значение из настроек, по умолчанию 60 секунд
        email_cooldown = getattr(settings, 'EMAIL_SEND_COOLDOWN', 60)

        # Проверяем, прошло ли время, указанное в конфиге
        if last_sent and time.time() - last_sent < email_cooldown:
            form.add_error("email", _("You can only request an email once every minute."))
            return self.form_invalid(form)

        user, created = User.objects.get_or_create(email=email)
        new_code = None

        if created:
            new_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            user.set_password(new_code)
            user.is_active = False  # Делаем пользователя неактивным до подтверждения
            user.save(update_fields=["password", "is_active"])

        if new_code or not user.is_active:
            # Генерируем токен для подтверждения
            token = secrets.token_urlsafe(16)
            cache.set(token, user.id, timeout=15 * 60)  # Сохраняем токен на 15 минут

            confirm_link = self.request.build_absolute_uri(
                reverse_lazy("web:register_confirm", kwargs={"token": token})
            )
            message = _(f"Follow this link to confirm your registration: {confirm_link}\n")
            if new_code:
                message += f"Your verification code and main code: {new_code}\n"

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
    user_id = cache.get(token)

    if not user_id:
        return redirect(to=reverse_lazy("web:register"))

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        code = request.POST.get("code")
        if code and user.check_password(code):
            user.is_active = True
            user.save(update_fields=["is_active"])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(to=reverse_lazy("web:profile"))
        else:
            return render(request, "registration/confirm.html", {"error": _("Invalid confirmation code.")})

    return render(request, "registration/confirm.html")



def index(request):
    return render(request, 'web/index.html')


class WebPasswordResetView(PasswordResetView):
    template_name = 'web/password_reset_email.html'
