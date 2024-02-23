from django import forms
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.forms.widgets import SelectDateWidget


class RegistForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名')
    birthdate = forms.DateField(label='生年月日', widget=SelectDateWidget(years=range(1900, 2023)))
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'birthdate', 'email', 'password']

    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user    

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')    
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
        