from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField

class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'captcha')

class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField()
    first_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'password1', 'captcha')

class CustomUserCreationByAdminForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password1', 'pic')


class CustomUserEditByAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'pic']


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'pic']


class CustomPasswordChangeForm(forms.Form):
    
    user = None
    new_password1 = forms.CharField(
        label=("New password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label=("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(
                    'The two password fields didn’t match.'
                )
        return cleaned_data

    def save(self):
        user = self.user
        user.set_password(self.cleaned_data['new_password1'])
        user.save()

