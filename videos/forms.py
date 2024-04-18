from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Video


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['name', 'video_url']


class VideoSearchForm(forms.Form):
    query = forms.CharField(label='Search Videos', max_length=100)