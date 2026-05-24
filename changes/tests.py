from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from .models import ChangeComment, ChangeRequest
from .services import (
    can_approve_change_request,
    can_edit_change_request,
    can_view_internal_comments,
)


class ChangeRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

    def test_change_request_creation(self):
        change_request = ChangeRequest.objects.create(
            title='Add dashboard metrics',
            change_type=ChangeRequest.TYPE_FEATURE,
            reason='Improve quality visibility.',
            current_state='No dashboard metrics.',
            proposed_change='Add chart-based quality dashboard.',
            business_impact='Better reporting.',
            technical_impact='New dashboard queries.',
            risk_level=ChangeRequest.RISK_MEDIUM,
            implementation_plan='Implement dashboard service.',
            testing_plan='Run unit and view tests.',
            rollback_plan='Revert dashboard commit.',
            requested_by=self.user,
        )

        self.assertEqual(change_request.status, ChangeRequest.STATUS_SUBMITTED)
        self.assertEqual(str(change_request), 'Add dashboard metrics (Submitted)')

    def test_high_risk_property(self):
        change_request = ChangeRequest.objects.create(
            title='Security fix',
            change_type=ChangeRequest.TYPE_SECURITY_FIX,
            reason='Fix access control.',
            current_state='Internal comments visible.',
            proposed_change='Restrict internal comments.',
            business_impact='Improves compliance.',
            technical_impact='Permission logic update.',
            risk_level=ChangeRequest.RISK_HIGH,
            implementation_plan='Update service permissions.',
            testing_plan='Test role access.',
            rollback_plan='Revert permission changes.',
            requested_by=self.user,
        )

        self.assertTrue(change_request.is_high_risk)

    def test_overdue_property(self):
        change_request = ChangeRequest.objects.create(
            title='Overdue change',
            change_type=ChangeRequest.TYPE_CONFIGURATION,
            reason='Improve release process.',
            current_state='Manual process.',
            proposed_change='Add rollback checklist.',
            business_impact='Reduced downtime.',
            technical_impact='Process documentation update.',
            risk_level=ChangeRequest.RISK_MEDIUM,
            implementation_plan='Update checklist.',
            testing_plan='Review with QA.',
            rollback_plan='Restore old checklist.',
            requested_by=self.user,
            target_release_date=timezone.now().date() - timedelta(days=1),
        )

        self.assertTrue(change_request.is_overdue)

    def test_approve_change_request(self):
        manager = User.objects.create_user(
            username='manager1',
            password='Testpass123'
        )
        manager.profile.role = Profile.ROLE_PROJECT_MANAGER
        manager.profile.save()

        change_request = ChangeRequest.objects.create(
            title='Approval test',
            change_type=ChangeRequest.TYPE_PROCESS,
            reason='Improve workflow.',
            current_state='No formal approval.',
            proposed_change='Add approval workflow.',
            business_impact='Better governance.',
            technical_impact='Workflow status update.',
            risk_level=ChangeRequest.RISK_LOW,
            implementation_plan='Add approve method.',
            testing_plan='Run model test.',
            rollback_plan='Revert approval method.',
            requested_by=self.user,
        )

        change_request.approve(manager, 'Approved for release.')

        self.assertEqual(change_request.status, ChangeRequest.STATUS_APPROVED)
        self.assertEqual(change_request.approved_by, manager)
        self.assertIsNotNone(change_request.approved_at)


class ChangeRequestPermissionTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        self.manager = User.objects.create_user(
            username='manager1',
            password='Testpass123'
        )
        self.manager.profile.role = Profile.ROLE_PROJECT_MANAGER
        self.manager.profile.save()

        self.change_request = ChangeRequest.objects.create(
            title='Permission test',
            change_type=ChangeRequest.TYPE_FEATURE,
            reason='Permission testing.',
            current_state='Basic access.',
            proposed_change='Role-based access.',
            business_impact='Improved governance.',
            technical_impact='Permission checks.',
            risk_level=ChangeRequest.RISK_MEDIUM,
            implementation_plan='Update permission service.',
            testing_plan='Run permission tests.',
            rollback_plan='Revert permission changes.',
            requested_by=self.student,
        )

    def test_requester_can_edit_submitted_change(self):
        self.assertTrue(
            can_edit_change_request(self.student, self.change_request)
        )

    def test_manager_can_approve_change_request(self):
        self.assertTrue(can_approve_change_request(self.manager))

    def test_student_cannot_approve_change_request(self):
        self.assertFalse(can_approve_change_request(self.student))

    def test_manager_can_view_internal_comments(self):
        self.assertTrue(can_view_internal_comments(self.manager))

    def test_student_cannot_view_internal_comments(self):
        self.assertFalse(can_view_internal_comments(self.student))


class ChangeRequestViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        self.change_request = ChangeRequest.objects.create(
            title='View test change',
            change_type=ChangeRequest.TYPE_FEATURE,
            reason='Testing views.',
            current_state='No test page.',
            proposed_change='Add view tests.',
            business_impact='Improves confidence.',
            technical_impact='Test client checks.',
            risk_level=ChangeRequest.RISK_LOW,
            implementation_plan='Write tests.',
            testing_plan='Run Django test.',
            rollback_plan='Remove test file.',
            requested_by=self.user,
        )

    def test_change_list_requires_login(self):
        response = self.client.get(reverse('changes:change_list'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_change_list(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.get(reverse('changes:change_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Change Requests')

    def test_logged_in_user_can_view_change_detail(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.get(
            reverse('changes:change_detail', args=[self.change_request.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View test change')

    def test_logged_in_user_can_create_comment(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.post(
            reverse('changes:change_detail', args=[self.change_request.id]),
            {'comment': 'This is a change comment.', 'is_internal': False}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ChangeComment.objects.filter(comment='This is a change comment.').exists()
        )