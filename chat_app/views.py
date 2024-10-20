# Create your views here.
# chat_app/views.py

from .tasks import generate_assessment

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, views as auth_views
from .forms import SignUpForm, ScenarioForm
from .models import UserProfile, Assignment, Conversation, Message, Scenario, Assessment
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
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

class LoginView(auth_views.LoginView):
    template_name = 'chat_app/login.html'

class LogoutView(auth_views.LogoutView):
    next_page = 'login'

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            is_teacher = form.cleaned_data.get('is_teacher')
            if is_teacher is None:
                is_teacher = False
            user_profile = user.userprofile
            user_profile.email = form.cleaned_data.get('email')
            user_profile.is_teacher = is_teacher
            user_profile.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
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
    return render(request, 'chat_app/student_dashboard.html', {'assignments': assignments})

@login_required
def teacher_dashboard(request):
    scenarios = Scenario.objects.filter(created_by=request.user.userprofile)
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
            student_user = User.objects.get(username=student_username)
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
        data = json.loads(request.body)
        active = data.get('active', False)
        scenario = Scenario.objects.get(pk=scenario_id)
        scenario.active = active
        scenario.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

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

@login_required
def chat_conversation(request, conversation_id):
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
            sender_name=request.user.username,
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
        try:
            user_profile = user.userprofile
            is_teacher = user_profile.is_teacher
        except UserProfile.DoesNotExist:
            # Handle the case where UserProfile does not exist
            # Redirect to a default page or raise an exception
            return reverse_lazy('login')

        if is_teacher:
            return reverse_lazy('teacher_dashboard')
        else:
            return reverse_lazy('student_dashboard')