# Create your models here.
# chat_app/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifiers for authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # You can add any additional fields here if needed
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    help_texts = {
            'email': None,
            'password1': None,
            'password2': None,
        }

    # Remove the username field
    username = None
    # Assign the custom user manager to objects
    objects = CustomUserManager()

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove `username` from required fields

    def __str__(self):
        return self.email

# Update your UserProfile to use CustomUser
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email

class Scenario(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    prompt = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='scenarios')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assigned_scenarios')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class Conversation(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='conversations')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    bot_context = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Conversation {self.id} for {self.assignment}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    sender_name = models.CharField(max_length=255)  # To store 'Bot' or student's name
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Assessment(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='assessment')
    assessment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment for Conversation {self.conversation.id}"
