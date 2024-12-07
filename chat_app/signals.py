# chat_app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile, Assignment, Scenario

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserProfile)
def assign_scenario_to_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_teacher:
        # Get or create the default scenario
        scenario_title = 'Default Scenario'  # Replace with your scenario title
        default_scenario, _ = Scenario.objects.get_or_create(
            title=scenario_title,
            defaults={
                'description': 'Default scenario description.',
                'prompt': 'Default prompt.',
                'is_active': True,
                'created_by': instance,  # Assign to the user or a default teacher
            }
        )
        # Create an assignment for the new user
        Assignment.objects.create(
            scenario=default_scenario,
            student=instance,
            assigned_by=None  # Or set to a default teacher's UserProfile
        )