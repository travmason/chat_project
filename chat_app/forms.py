# chat_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Scenario
from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('Name', css_class='form-control', wrapper_class='form-group', placeholder='Enter your name'),
            Field('email'),
            Field('password1', css_class='form-control', wrapper_class='form-group', placeholder='Enter your password', help_text=None),
            Field('password2', css_class='form-control', wrapper_class='form-group', placeholder='Confirm your password', help_text=None),
            Submit('signup', 'Sign up', css_class='btn btn-primary')
        )
        # Remove help texts
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
