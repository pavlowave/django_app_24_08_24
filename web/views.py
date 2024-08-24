from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from core.models import Pan
from web.forms import PanConfirmDelete

from web.forms import RegisterForm


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
    return render(request, 'web/profile.html')

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy("web:profile")
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

def index(request):
    return render(request, 'web/index.html')


class WebPasswordResetView(PasswordResetView):
    template_name = 'web/password_reset_email.html'
