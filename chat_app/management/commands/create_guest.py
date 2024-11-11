import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create user groups and assign permissions.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.NOTICE('Got into create_guest user.'))

            # Import the User model
            User = get_user_model()

            # Check if the guest user already exists to avoid duplication
            if not User.objects.filter(username='guest').exists():
                guest_user = User.objects.create_user(username='guest', password='guest_password')
                guest_user.is_active = True  # Ensure the guest user is active
                guest_user.save()
                # Add the guest user to the guest group
                guest_group = Group.objects.get(name='Guest')
                guest_user.groups.add(guest_group)
                logger.info('Guest user created and added to the Guest group.')
                self.stdout.write(self.style.SUCCESS('Guest user created and added to the Guest group.'))

        except Exception as e:
            logger.critical(f"Unhandled exception in create_groups command: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Unhandled exception: {e}"))