# Create your models here.
# chat_app/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Scenario(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
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
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    bot_context = models.TextField(blank=True, null=True)  # Add this field

    def __str__(self):
        return f"Conversation {self.id} for {self.assignment}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    sender_name = models.CharField(max_length=255)  # To store 'Bot' or student's name
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Assessment(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE)
    assessment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
