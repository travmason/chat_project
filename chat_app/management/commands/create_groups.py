# your_app_name/management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, ContentType

class Command(BaseCommand):
    help = 'Create user groups and assign permissions.'

    def handle(self, *args, **options):
        # Define group names
        group_names = ['Admin', 'Teacher', 'Student', 'ContentCreator']

        for group_name in group_names:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created.'))
            else:
                self.stdout.write(f'Group "{group_name}" already exists.')

        # Assign all permissions to Admin group
        admin_group = Group.objects.get(name='Admin')
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        admin_group.save()
        self.stdout.write(self.style.SUCCESS('All permissions assigned to Admin group.'))

        # Assign permissions to Teacher group
        teacher_group = Group.objects.get(name='Teacher')
        teacher_models = ['assignment', 'conversation', 'message', 'assessment']
        content_types = ContentType.objects.filter(app_label='chat_app', model__in=teacher_models)
        teacher_permissions = Permission.objects.filter(content_type__in=content_types)
        teacher_group.permissions.set(teacher_permissions)
        teacher_group.save()
        self.stdout.write(self.style.SUCCESS('Permissions assigned to Teacher group.'))

        # Assign permissions to ContentCreator group
        content_group = Group.objects.get(name='ContentCreator')
        content_creator_models = ['assignment', 'scenario']
        content_types = ContentType.objects.filter(app_label='chat_app', model__in=content_creator_models)
        content_permissions = Permission.objects.filter(content_type__in=content_types)
        content_group.permissions.set(content_permissions)
        content_group.save()
        self.stdout.write(self.style.SUCCESS('Permissions assigned to ContentCreator group.'))