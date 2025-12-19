from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Обязательное поле. Введите действующий email.")

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
