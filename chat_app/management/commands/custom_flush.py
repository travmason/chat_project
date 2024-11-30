from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Custom flush with CASCADE"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
            TRUNCATE "django_session", "auth_group", "chat_app_conversation", 
            "django_content_type", "chat_app_scenario", "auth_group_permissions", 
            "chat_app_userprofile", "auth_permission", "chat_app_message", 
            "django_admin_log", "chat_app_assignment", "chat_app_assessment", 
            "auth_user_groups" RESTART IDENTITY CASCADE;
            """)
        self.stdout.write(self.style.SUCCESS('Database flushed successfully.'))