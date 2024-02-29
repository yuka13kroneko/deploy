from django import forms
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.forms.widgets import SelectDateWidget
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password


class RegistForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名')
    birthdate = forms.DateField(label='生年月日', widget=SelectDateWidget(years=range(1900, 2023)))
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'birthdate', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')

        if password:
            try:
                validate_password(password, self.instance)  # パスワードのバリデーション
            except ValidationError as e:
            # バリデーションエラーがあればエラーメッセージを設定
                for message in e.messages:
                    self.add_error('password', message)

        return cleaned_data

    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
    

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')    
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

