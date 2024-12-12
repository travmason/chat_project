# chat_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.models import User
from .models import Scenario
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the help text, but keep validators intact
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

class SignUpForm(UserCreationForm):
    # is_teacher = forms.BooleanField(required=False, label='Are you a teacher?')
    is_teacher = False
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['title', 'description', 'prompt']
