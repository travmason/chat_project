# chat_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Scenario

class SignUpForm(UserCreationForm):
    is_teacher = forms.BooleanField(required=False, label='Are you a teacher?')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_teacher')

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['title', 'description', 'prompt']
