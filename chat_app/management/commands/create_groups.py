import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, ContentType
from django.core.exceptions import ObjectDoesNotExist

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create user groups and assign permissions.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.NOTICE('Got into create_groups.'))

            # Define group names
            group_names = ['Admin', 'Teacher', 'Student', 'ContentCreator', 'Guest']

            # Create groups
            for group_name in group_names:
                try:
                    group, created = Group.objects.get_or_create(name=group_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created.'))
                    else:
                        self.stdout.write(f'Group "{group_name}" already exists.')
                except Exception as e:
                    logger.error(f"Failed to create or get group '{group_name}': {e}")
                    self.stdout.write(self.style.ERROR(f"Failed to create or get group '{group_name}': {e}"))

            # Assign all permissions to Admin group
            try:
                admin_group = Group.objects.get(name='Admin')
                all_permissions = Permission.objects.all()
                admin_group.permissions.set(all_permissions)
                admin_group.save()
                self.stdout.write(self.style.SUCCESS('All permissions assigned to Admin group.'))
            except ObjectDoesNotExist as e:
                logger.error(f"Admin group not found: {e}")
                self.stdout.write(self.style.ERROR(f"Admin group not found: {e}"))
            except Exception as e:
                logger.error(f"Failed to assign permissions to Admin group: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to assign permissions to Admin group: {e}"))

            # Assign permissions to Teacher group
            try:
                teacher_group = Group.objects.get(name='Teacher')
                teacher_models = ['assignment', 'conversation', 'message', 'assessment']
                content_types = ContentType.objects.filter(app_label='chat_app', model__in=teacher_models)
                teacher_permissions = Permission.objects.filter(content_type__in=content_types)
                teacher_group.permissions.set(teacher_permissions)
                teacher_group.save()
                self.stdout.write(self.style.SUCCESS('Permissions assigned to Teacher group.'))
            except ObjectDoesNotExist as e:
                logger.error(f"Teacher group or related permissions not found: {e}")
                self.stdout.write(self.style.ERROR(f"Teacher group or related permissions not found: {e}"))
            except Exception as e:
                logger.error(f"Failed to assign permissions to Teacher group: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to assign permissions to Teacher group: {e}"))

            # Assign permissions to ContentCreator group
            try:
                content_group = Group.objects.get(name='Guest')
                content_creator_models = ['conversation', 'message', 'assessment']
                content_types = ContentType.objects.filter(app_label='chat_app', model__in=content_creator_models)
                content_permissions = Permission.objects.filter(content_type__in=content_types)
                content_group.permissions.set(content_permissions)
                content_group.save()
                self.stdout.write(self.style.SUCCESS('Permissions assigned to ContentCreator group.'))
            except ObjectDoesNotExist as e:
                logger.error(f"ContentCreator group or related permissions not found: {e}")
                self.stdout.write(self.style.ERROR(f"ContentCreator group or related permissions not found: {e}"))
            except Exception as e:
                logger.error(f"Failed to assign permissions to ContentCreator group: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to assign permissions to ContentCreator group: {e}"))

            # Assign permissions to Guest group
            try:
                guest_group = Group.objects.get(name='Guest')
                guest_models = ['assignment', 'scenario']
                guest_types = ContentType.objects.filter(app_label='chat_app', model__in=guest_models)
                guest_permissions = Permission.objects.filter(content_type__in=guest_types)
                guest_group.permissions.set(guest_permissions)
                guest_group.save()
                self.stdout.write(self.style.SUCCESS('Permissions assigned to Guest group.'))
            except ObjectDoesNotExist as e:
                logger.error(f"Guest group or related permissions not found: {e}")
                self.stdout.write(self.style.ERROR(f"Guest group or related permissions not found: {e}"))
            except Exception as e:
                logger.error(f"Failed to assign permissions to Guest group: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to assign permissions to Guest group: {e}"))

        except Exception as e:
            logger.critical(f"Unhandled exception in create_groups command: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Unhandled exception: {e}"))