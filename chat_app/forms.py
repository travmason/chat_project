# chat_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Scenario
from allauth.account.forms import SignupForm, LoginForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text for specific fields
        if 'login' in self.fields:
            self.fields['login'].help_text = ''
        if 'password' in self.fields:
            self.fields['password'].help_text = ''

        # Add custom classes, placeholders, etc.
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class CustomSignupForm(SignupForm):
    name = forms.CharField(label="Name", max_length=150, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control', wrapper_class='form-group', placeholder='Enter your name'),
            Field('email'),
            Field('password1', css_class='form-control', wrapper_class='form-group', placeholder='Enter your password', help_text=None),
            Field('password2', css_class='form-control', wrapper_class='form-group', placeholder='Confirm your password', help_text=None),
            Submit('signup', 'Sign up', css_class='btn btn-primary')
        )
        # Remove help texts
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['name'].widget.attrs.update({"placeholder": "Enter your preferred display name", "class": "form-control"})
        
    def signup(self, request, user):
        nm = self.cleaned_data.get("name", "").strip()
        if nm:
            if hasattr(user, "name"):
                user.name = nm
            else:
                first, *rest = nm.split(" ", 1)
                user.first_name = first
                user.last_name = rest[0] if rest else ""
        user.save()
        return user

class SignUpForm(UserCreationForm):
    # is_teacher = forms.BooleanField(required=False, label='Are you a teacher?')
    is_teacher = False
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['title', 'description', 'developer', 'is_active', 'is_free']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'developer': 'Prompt',
            'is_active': 'Set Active',
            'is_free': 'Available on Free Tier',
        }
