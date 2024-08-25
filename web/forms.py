from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from core.models import Pan

# Получаем модель пользователя через get_user_model
User = get_user_model()


class PanForm(forms.ModelForm):
    class Meta:
        model = Pan
        fields = ["price", "vendor", "diameter"]


class PanConfirmDelete(forms.Form):
    confirm_delete = forms.BooleanField(required=False)

    def clean(self):
        if self.cleaned_data["confirm_delete"] is False:
            raise ValidationError("You must confirm this form!")
        return super(PanConfirmDelete, self).clean()


class RegisterForm(forms.Form):
    confirmation = forms.BooleanField(widget=forms.RadioSelect(attrs={"class": "form-control;"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control;"}))

    def clean_confirmation(self):
        if self.cleaned_data["confirmation"] is not True:
            raise ValidationError("You must confirm!")
