from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # If both present and they don't match, skip other checks.
        # We'll raise the clear mismatch message in clean().
        if password1 and password2 and password1 != password2:
            return password2

        # Only run length/security checks when passwords match or password1 is missing.
        if password2:
            if len(password2) < 8:
                raise ValidationError("This password is too short. It must contain at least 8 characters.")
            common_passwords = ['password', '12345678', 'qwerty', 'letmein', '123456']
            if password2.lower() in common_passwords:
                raise ValidationError("This password is not secure.")
        return password2

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            # non-field error, shows as single message
            raise ValidationError("Password and Confirm Password do not match.")
        return cleaned



class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
