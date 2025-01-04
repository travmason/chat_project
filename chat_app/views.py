# Create your views here.
# chat_app/views.py

from .tasks import generate_assessment

import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, views as auth_views
from .forms import SignUpForm, ScenarioForm, CustomSignupForm
from .models import UserProfile, Assignment, Conversation, Message, Scenario, Assessment
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
from django_ratelimit.decorators import ratelimit
# from ratelimit.exceptions import Ratelimited
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from openai import OpenAI
import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

# Set the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# True if not in os.environ because of casting above
DEBUG = env('DEBUG')

# Raises Django's ImproperlyConfigured
# exception if KEY not in os.environ
OPENAI_API_KEY = env('OPENAI_API_KEY')

# create OpenAI client object
client = OpenAI(api_key=OPENAI_API_KEY)

#Grab the User using get_user_model() instead of importing the User model directly. This is a best practice where a custom user model is in use.
User = get_user_model()

class LoginView(auth_views.LoginView):
    template_name = 'chat_app/login.html'

class LogoutView(auth_views.LogoutView):
    next_page = 'login'

def privacy(request):
    return render(request, 'chat_app/privacy.html')

def tos(request):
    return render(request, 'chat_app/tos.html')

# Won't work as the allowed host changes constaltly for the EB environment.
# def health_check(request):
#     return HttpResponse('OK')

def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse('Sorry you are blocked', status=429)
    return HttpResponseForbidden('Forbidden')


def google_login_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = data.get('token')
        if not token:
            return HttpResponseBadRequest("No token provided.")
        
        # Verify token with Google
        # This will raise ValueError if the token is invalid
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # idinfo will typically contain fields like:
        # {
        #   "iss": "accounts.google.com",
        #   "azp": "<client_id>",
        #   "aud": "<client_id>",
        #   "sub": "<Google user's unique ID>",
        #   "email": "user@example.com",
        #   "email_verified": True,
        #   "name": "User Name",
        #   "picture": "URL to profile image",
        #   "given_name": "User",
        #   "family_name": "Name",
        #   ... other fields ...
        # }

        # Check the token issuer and audience
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return HttpResponseBadRequest("Invalid token issuer.")

        # Extract the required information
        email = idinfo.get('email')
        email_verified = idinfo.get('email_verified')
        name = idinfo.get('name', '')
        sub = idinfo.get('sub')  # Unique Google account identifier

        if not email or not email_verified:
            return HttpResponseBadRequest("Email not present or not verified.")

        # Try to get the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create a new user if one does not exist
            # Depending on your user model, you may need to set a username.
            # If using the default Django user model, username is required, 
            # you can set it to the email or a unique string.
            user = User.objects.create_user(
                email=email,
                password=None,  # No password, user logs in via Google only
                first_name=name.split(' ')[0],
                last_name=' '.join(name.split(' ')[1:])
            )
            user.set_unusable_password()  # Ensure the user cannot log in with a password
            user.save()
            # Optionally store the Google sub in a user profile if you have one.
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'google_sub': sub}
            )
            if not created:
                user_profile.google_sub = sub
                user_profile.save()

        # At this point, we have a user object (existing or newly created)
        # Log them in
        # Since we trust Google verification, we can just call login().
        # If you prefer, you could wrap this in a custom authentication backend.
        login(request, user)

        return JsonResponse({"status": "success"})
    except ValueError:
        # Thrown if token verification failed
        return HttpResponseBadRequest("Invalid token.")
    except KeyError:
        # If expected fields like email or sub are missing
        return HttpResponseBadRequest("Malformed token response.")

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            new_user = form.save()
            # Retrieve additional data from the form
            is_teacher = form.cleaned_data.get('is_teacher', False)
            email = form.cleaned_data.get('email')
            # Update the UserProfile
            user_profile = new_user.userprofile
            user_profile.email = email
            user_profile.is_teacher = is_teacher
            user_profile.save()
            # Authenticate the user
            raw_password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(request, email=email, password=raw_password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('dashboard')
            else:
                # Handle authentication failure
                return render(request, 'chat_app/signup.html', {
                    'form': form,
                    'error': 'Authentication failed. Please try again.',
                })
    else:
        form = CustomSignupForm()
    return render(request, 'chat_app/signup.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.userprofile.is_teacher:
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')
    
def landing(request):
    return render(request, 'index.html')

@login_required
def student_dashboard(request):
    assignments = Assignment.objects.filter(student=request.user.userprofile).prefetch_related('conversations')
    user_attributes = dir(request.user)
    return render(request, 'chat_app/student_dashboard.html', {'assignments': assignments, 'user': request.user, 'user_attributes': user_attributes})

@login_required
def teacher_dashboard(request):
    scenarios = Scenario.objects.all()
    # scenarios = Scenario.objects.filter(created_by=request.user.userprofile)
    assignments = Assignment.objects.filter(assigned_by=request.user.userprofile)
    return render(request, 'chat_app/teacher_dashboard.html', {'scenarios': scenarios, 'assignments': assignments})

@login_required
def create_scenario(request):
    if not request.user.userprofile.is_teacher:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ScenarioForm(request.POST)
        if form.is_valid():
            scenario = form.save(commit=False)
            scenario.created_by = request.user.userprofile
            scenario.save()
            return redirect('teacher_dashboard')
    else:
        form = ScenarioForm()
    return render(request, 'chat_app/create_scenario.html', {'form': form})

@login_required
def assign_scenario(request):
    if not request.user.userprofile.is_teacher:
        return redirect('dashboard')
    if request.method == 'POST':
        scenario_id = request.POST.get('scenario_id')
        student_username = request.POST.get('student_username')
        print(scenario_id, student_username)
        scenario = get_object_or_404(Scenario, id=scenario_id)
        try:
            student_user = User.objects.get(email=student_username)
            student_profile = student_user.userprofile
            Assignment.objects.create(
                scenario=scenario,
                student=student_profile,
                assigned_by=request.user.userprofile
            )
            return redirect('teacher_dashboard')
        except User.DoesNotExist:
            error = "Student not found."
            return render(request, 'chat_app/assign_scenario.html', {'error': error})
    else:
        scenarios = Scenario.objects.filter(created_by=request.user.userprofile, is_active=True)
        users = User.objects.filter(userprofile__is_teacher=False)
        return render(request, 'chat_app/assign_scenario.html', {'scenarios': scenarios, 'users': users})

@login_required
def unassign_scenario(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Ensure that only teachers can unassign scenarios
    if not request.user.userprofile.is_teacher:
        messages.error(request, "You do not have permission to unassign this scenario.")
        return redirect('dashboard')

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Scenario unassigned successfully.")
        return redirect('teacher_dashboard')

    return render(request, 'chat_app/unassign_scenario_confirm.html', {'assignment': assignment})

@login_required
def toggle_scenario(request, scenario_id):
    if request.method == "POST":
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            active = data.get('active', False)

            # Fetch the scenario
            scenario = get_object_or_404(Scenario, pk=scenario_id)

            # Update the active status
            scenario.is_active = active
            scenario.save()

            return JsonResponse({'success': True})
        except Exception as e:
            # Log the exception for debugging
            print(f"Error toggling scenario: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@login_required
def delete_scenario(request, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id)

    # Ensure that only teachers or admins can delete scenarios
    if not request.user.userprofile.is_teacher and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this scenario. How did you even get here? Cheeky.")
        return redirect('dashboard')

    if request.method == 'POST':
        scenario.delete()
        messages.success(request, "Scenario deleted successfully.")
        return redirect('scenario_list')

    return render(request, 'chat_app/delete_scenario_confirm.html', {'scenario': scenario})

def onetimetrial(request):
    return render(request, 'chat_app/trial.html')

@login_required
def start_conversation(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user.userprofile != assignment.student:
        return redirect('dashboard')

    # Create a new conversation
    conversation = Conversation.objects.create(
        assignment=assignment,
        bot_context=f"You are acting as a customer in the following scenario: {assignment.scenario.description}"
    )

    # Redirect to the chat view for the new conversation
    return redirect('chat_conversation', conversation_id=conversation.id)

get_rate = lambda g, r: '20/m' if r.user.is_authenticated else '5/m'
@login_required
@ratelimit(key='ip', rate=get_rate, method=ratelimit.UNSAFE, block=False)
def chat_conversation(request, conversation_id):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # here we want to set up the bot_reply message to just be a static message saying that the user is rate limited
        bot_message = Message.objects.create(
            conversation=conversation,
            sender=None,  # No sender for bot
            sender_name='Customer',
            message="You are sending messages too quickly. Please wait a minute before sending another message."
        )


        # Prepare JSON response
        data = {
            'student_message': {
                'sender_name': "Mr Speedy",
                'message': "I'm typing too fast!",
            },
            'bot_reply': {
                'sender_name': bot_message.sender_name,
                'message': bot_message.message,
            }
        }

        return JsonResponse(data)
        # return JsonResponse({'error': 'try again in 1 minute'}, status=429)

    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if the user is authorized
    if request.user.userprofile != conversation.assignment.student:
        return redirect('dashboard')

    if not conversation.is_active:
        return redirect('student_dashboard')

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_message = request.POST.get('message')

        # Save the student's message
        student_message = Message.objects.create(
            conversation=conversation,
            sender=request.user.userprofile,
            sender_name=request.user.email,
            message=user_message
        )

        # Prepare messages for the API
        messages = [
            {"role": "system", "content": conversation.bot_context},
        ]

        # Get previous messages
        previous_messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        for msg in previous_messages:
            if msg.sender == request.user.userprofile:
                messages.append({"role": "user", "content": msg.message})
            else:
                messages.append({"role": "assistant", "content": msg.message})

        # Call OpenAI API

        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=messages)

        bot_reply = response.choices[0].message.content.strip()

        # Save bot's reply
        bot_message = Message.objects.create(
            conversation=conversation,
            sender=None,  # No sender for bot
            sender_name='Customer',
            message=bot_reply
        )

        # Prepare JSON response
        data = {
            'student_message': {
                'sender_name': student_message.sender_name,
                'message': student_message.message,
            },
            'bot_reply': {
                'sender_name': bot_message.sender_name,
                'message': bot_message.message,
            }
        }

        return JsonResponse(data)

    # Get all messages for display
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    return render(request, 'chat_app/chat.html', {'conversation': conversation, 'messages': messages})

@login_required
def end_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if the user is the student associated with the conversation
    if request.user.userprofile != conversation.assignment.student:
        return redirect('dashboard')

    # End the conversation
    conversation.is_active = False
    conversation.ended_at = timezone.now()
    conversation.save()

    # Trigger assessment generation (asynchronously using Celery)
    generate_assessment.delay(conversation.id)

    # Redirect to the student's dashboard or an assessment page
    #return redirect('student_dashboard')  # Or redirect to 'view_assessment' if preferred
    return redirect('view_assessment', conversation_id=conversation.id)  # Or redirect to 'student_dashboard' if preferred

@login_required
def view_assessment(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if the user is authorized to view the assessment
    if request.user.userprofile != conversation.assignment.student:
        return redirect('dashboard')

    try:
        assessment = conversation.assessment
    except Assessment.DoesNotExist:
        assessment = None

    return render(request, 'chat_app/assessment.html', {'assessment': assessment})

class CustomLoginView(LoginView):
    template_name = 'chat_app/login.html'

    def get_success_url(self):
        user = self.request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        is_teacher = user_profile.is_teacher

        if is_teacher:
            return reverse_lazy('teacher_dashboard')
        else:
            return reverse_lazy('student_dashboard')