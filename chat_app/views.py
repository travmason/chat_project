# Create your views here.
# chat_app/views.py

from .tasks import generate_assessment

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, views as auth_views
from .forms import SignUpForm, ScenarioForm
from .models import UserProfile, Assignment, Conversation, Message, Scenario
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User

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
            user_profile = user.userprofile
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

@login_required
def student_dashboard(request):
    assignments = Assignment.objects.filter(student=request.user.userprofile)
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
        scenarios = Scenario.objects.filter(created_by=request.user.userprofile)
        return render(request, 'chat_app/assign_scenario.html', {'scenarios': scenarios})

@login_required
def start_conversation(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user.userprofile != assignment.student:
        return redirect('dashboard')

    # Get or create the conversation
    conversation, created = Conversation.objects.get_or_create(
        assignment=assignment, is_active=True
    )

    # Initialize bot context if conversation is new
    if created or not conversation.bot_context:
        scenario = assignment.scenario
        conversation.bot_context = f"You are acting as a customer in the following scenario: {scenario.description}"
        conversation.save()

    if request.method == 'POST':
        user_message = request.POST.get('message')

        # Save the student's message
        Message.objects.create(
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
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        bot_reply = response['choices'][0]['message']['content'].strip()

        # Save bot's reply
        Message.objects.create(
            conversation=conversation,
            sender=None,  # No sender for bot
            sender_name='Customer',
            message=bot_reply
        )

        return redirect('start_conversation', assignment_id=assignment_id)

    # Get all messages for display
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    return render(request, 'chat_app/chat.html', {'conversation': conversation, 'messages': messages})


@login_required
def end_conversation(request, assignment_id):
    conversation = get_object_or_404(Conversation, assignment__id=assignment_id, is_active=True)
    if request.user.userprofile != conversation.assignment.student:
        return redirect('dashboard')

    conversation.is_active = False
    conversation.ended_at = timezone.now()
    conversation.save()

    # Trigger assessment generation
    generate_assessment.delay(conversation.id)

    return redirect('student_dashboard')

@login_required
def view_assessment(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user.userprofile != conversation.assignment.student:
        return redirect('dashboard')

    try:
        assessment = conversation.assessment
    except Assessment.DoesNotExist:
        assessment = None

    return render(request, 'chat_app/assessment.html', {'assessment': assessment})
