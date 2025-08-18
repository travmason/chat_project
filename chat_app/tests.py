import os
import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import (
    UserProfile,
    Scenario,
    Assignment,
    Conversation,
    Message,
)


# Ensure required environment variables are present for module imports that
# expect them. The values here are placeholders used only for testing.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("GPT_CONVERSATION_MODEL", "test-model")
os.environ.setdefault("GPT_ASSESSMENT_MODEL", "test-model")


class BaseTestCase(TestCase):
    """Common set up creating a teacher and a student user."""

    def setUp(self):
        self.User = get_user_model()

        # Teacher user used for scenario creation and assignments
        self.teacher = self.User.objects.create_user(
            email="teacher@example.com", password="pass"
        )
        self.teacher.userprofile.is_teacher = True
        self.teacher.userprofile.save()

        # Regular student user
        self.student = self.User.objects.create_user(
            email="student@example.com", password="pass"
        )

        self.client = Client()


class UserModelTests(BaseTestCase):
    def test_user_profile_created_and_default_assignment(self):
        """Creating a user automatically creates a profile and assignment."""
        user = self.User.objects.create_user(
            email="newstudent@example.com", password="pass"
        )
        profile_exists = UserProfile.objects.filter(user=user).exists()
        assignment_exists = Assignment.objects.filter(student=user.userprofile).exists()

        self.assertTrue(profile_exists)
        self.assertTrue(assignment_exists)

    def test_superuser_creation_has_no_assignment(self):
        """Superuser should have profile but no default assignment."""
        admin = self.User.objects.create_superuser(
            email="admin@example.com", password="pass"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(UserProfile.objects.filter(user=admin).exists())
        self.assertEqual(
            Assignment.objects.filter(student=admin.userprofile).count(), 0
        )


class ScenarioAssignmentTests(BaseTestCase):
    def test_teacher_can_assign_scenario_to_student(self):
        scenario = Scenario.objects.create(
            title="Scenario 1",
            description="desc",
            created_by=self.teacher.userprofile,
        )

        self.client.login(email="teacher@example.com", password="pass")
        response = self.client.post(
            reverse("assign_scenario"),
            {"scenario_id": scenario.id, "student_username": self.student.email},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Assignment.objects.filter(
                scenario=scenario, student=self.student.userprofile
            ).exists()
        )

    def test_student_cannot_access_assign_view(self):
        self.client.login(email="student@example.com", password="pass")
        response = self.client.get(reverse("assign_scenario"))
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)


class SelfAssignScenarioTests(BaseTestCase):
    def test_self_assign_respects_limit(self):
        self.client.login(email="student@example.com", password="pass")

        # Pre-create two free assignments for the student
        for idx in range(2):
            scen = Scenario.objects.create(
                title=f"Free {idx}",
                description="desc",
                created_by=self.teacher.userprofile,
                is_free=True,
            )
            Assignment.objects.create(
                scenario=scen,
                student=self.student.userprofile,
                assigned_by=self.teacher.userprofile,
            )

        third = Scenario.objects.create(
            title="Free 2",
            description="desc",
            created_by=self.teacher.userprofile,
            is_free=True,
        )
        fourth = Scenario.objects.create(
            title="Free 3",
            description="desc",
            created_by=self.teacher.userprofile,
            is_free=True,
        )

        # Third assignment should succeed
        success = self.client.post(reverse("self_assign_scenario", args=[third.id]))
        self.assertEqual(success.status_code, 200)
        self.assertTrue(
            Assignment.objects.filter(
                scenario=third, student=self.student.userprofile
            ).exists()
        )

        # Fourth should fail due to limit
        fail = self.client.post(reverse("self_assign_scenario", args=[fourth.id]))
        self.assertEqual(fail.status_code, 500)
        payload = json.loads(fail.content.decode())
        self.assertFalse(payload["success"])


class ConversationFlowTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.scenario = Scenario.objects.create(
            title="Chat Scenario",
            description="desc",
            created_by=self.teacher.userprofile,
        )
        self.assignment = Assignment.objects.create(
            scenario=self.scenario,
            student=self.student.userprofile,
            assigned_by=self.teacher.userprofile,
        )

    def test_start_conversation_creates_conversation(self):
        self.client.login(email="student@example.com", password="pass")
        response = self.client.get(
            reverse("start_conversation", args=[self.assignment.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Conversation.objects.filter(assignment=self.assignment).exists()
        )

    @patch("chat_app.views.client")
    def test_chat_conversation_returns_bot_reply(self, mock_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Bot reply"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        conversation = Conversation.objects.create(
            assignment=self.assignment
        )

        self.client.login(email="student@example.com", password="pass")
        response = self.client.post(
            reverse("chat_conversation", args=[conversation.id]),
            {"message": "Hello"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["bot_reply"]["message"], "Bot reply")
        self.assertTrue(
            Message.objects.filter(
                conversation=conversation, sender=self.student.userprofile
            ).exists()
        )

    @patch("chat_app.views.generate_assessment.delay")
    def test_end_conversation_triggers_assessment(self, mock_delay):
        conversation = Conversation.objects.create(
            assignment=self.assignment
        )

        self.client.login(email="student@example.com", password="pass")
        response = self.client.get(
            reverse("end_conversation", args=[conversation.id])
        )

        conversation.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(conversation.is_active)
        self.assertIsNotNone(conversation.ended_at)
        mock_delay.assert_called_once_with(conversation.id)

