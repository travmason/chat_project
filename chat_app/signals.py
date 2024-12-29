# chat_app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile, Assignment, Scenario

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    1. Create a UserProfile whenever a new User is created.
    2. We explicitly skip creating an assignment here if the User is a superuser
       or is_staff (depending on how you treat 'teacher' vs. staff).
       We’ll handle the assignment creation in the other signal.
    """
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            # Log or handle unexpected errors creating a profile
            print(f"Error creating UserProfile for user {instance.username}: {e}")



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
        
    """
    Assign a 'Default Scenario' to new non-teacher users. Use the first available
    superuser as the 'assigned_by'. If no superuser is found, log an error or skip.
    Also skip if this user is a superuser or is_teacher.
    """
    # 1. Only proceed if this UserProfile is newly created
    #    and the user is NOT a teacher or superuser.
    if not created:
        return

    if instance.is_teacher or instance.user.is_superuser:
        # Skip creating assignments for teachers or superusers
        return

    scenario_title = 'Default Scenario'
    try:
        # 2. Get or create the default scenario
        default_scenario, _ = Scenario.objects.get_or_create(
            title=scenario_title,
            defaults={
                'description': 'Default scenario description.',
                'prompt': 'Default prompt.',
                'is_active': True,
                # We can set created_by to the new user if you like
                # or to the superuser (but often it's the user themselves).
                'created_by': instance,
            }
        )

        # 3. Find a default superuser for assigned_by
        #    If none exists, handle gracefully (log, raise, etc.)
        default_superuser = User.objects.filter(is_superuser=True).first()
        if not default_superuser:
            # If you choose to skip assignment creation in this case, do so:
            print("No superuser found! Skipping assignment creation.")
            return

        # 4. Retrieve the superuser's UserProfile
        default_superuser_profile = UserProfile.objects.get(user=default_superuser)

        # 5. Create the assignment
        Assignment.objects.create(
            scenario=default_scenario,
            student=instance,
            assigned_by=default_superuser_profile
        )

    except Exception as e:
        # Catch any unexpected errors (e.g., DB issues, concurrency)
        print(f"Error creating default assignment for user {instance.user.username}: {e}")