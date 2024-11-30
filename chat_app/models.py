# Create your models here.
# chat_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Remove the username field
    username = None

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove `username` from required fields

    def __str__(self):
        return self.email

# Update your UserProfile to use CustomUser
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
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
