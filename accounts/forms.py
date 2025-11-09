from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import CustomUser
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
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
            raise ValidationError("Password and Confirm Password do not match.")
        return cleaned

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'admin':
            raise ValidationError("You cannot register as an Admin.")
        return role


class CustomLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password.")
        return cleaned

# this is for reset password


class CustomSetPasswordForm(SetPasswordForm):
    def clean(self):
        cleaned_data = super().clean()
        new_password2 = cleaned_data.get("new_password2")

        if new_password2 and self.user.check_password(new_password2):
            raise ValidationError("You cannot reuse your old password. Please choose a new one.")

        return cleaned_data

from django import forms
from .models import CustomUser


# for profile picture
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
