from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from .models import IssueComment, IssueHistory, QualityIssue
from .services import can_edit_issue, can_view_internal_comments


class QualityIssueModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

    def test_quality_issue_creation(self):
        issue = QualityIssue.objects.create(
            title='Login error',
            description='Login page does not show correct message.',
            issue_type=QualityIssue.TYPE_BUG,
            severity=QualityIssue.SEVERITY_MEDIUM,
            priority=QualityIssue.PRIORITY_HIGH,
            affected_system='Authentication Module',
            reported_by=self.user,
        )

        self.assertEqual(issue.status, QualityIssue.STATUS_SUBMITTED)
        self.assertEqual(str(issue), 'Login error (Submitted)')

    def test_issue_overdue_property_returns_true(self):
        issue = QualityIssue.objects.create(
            title='Overdue issue',
            description='Issue is overdue.',
            issue_type=QualityIssue.TYPE_INCIDENT,
            severity=QualityIssue.SEVERITY_HIGH,
            priority=QualityIssue.PRIORITY_URGENT,
            affected_system='Dashboard',
            reported_by=self.user,
            due_date=timezone.now().date() - timedelta(days=1),
        )

        self.assertTrue(issue.is_overdue)

    def test_issue_overdue_property_returns_false_for_closed_issue(self):
        issue = QualityIssue.objects.create(
            title='Closed issue',
            description='Closed issue should not be overdue.',
            issue_type=QualityIssue.TYPE_INCIDENT,
            severity=QualityIssue.SEVERITY_HIGH,
            priority=QualityIssue.PRIORITY_URGENT,
            affected_system='Dashboard',
            reported_by=self.user,
            due_date=timezone.now().date() - timedelta(days=1),
            status=QualityIssue.STATUS_CLOSED,
        )

        self.assertFalse(issue.is_overdue)

    def test_mark_resolved_updates_status_and_summary(self):
        issue = QualityIssue.objects.create(
            title='Bug fix',
            description='Bug needs to be fixed.',
            issue_type=QualityIssue.TYPE_BUG,
            severity=QualityIssue.SEVERITY_MEDIUM,
            priority=QualityIssue.PRIORITY_HIGH,
            affected_system='Issue Module',
            reported_by=self.user,
        )

        issue.mark_resolved('Bug fixed and tested.')

        self.assertEqual(issue.status, QualityIssue.STATUS_RESOLVED)
        self.assertEqual(issue.resolution_summary, 'Bug fixed and tested.')
        self.assertIsNotNone(issue.resolved_at)

    def test_close_issue_updates_status(self):
        issue = QualityIssue.objects.create(
            title='Close issue',
            description='Issue should close.',
            issue_type=QualityIssue.TYPE_BUG,
            severity=QualityIssue.SEVERITY_LOW,
            priority=QualityIssue.PRIORITY_LOW,
            affected_system='Issue Module',
            reported_by=self.user,
        )

        issue.close_issue()

        self.assertEqual(issue.status, QualityIssue.STATUS_CLOSED)
        self.assertIsNotNone(issue.closed_at)


class QualityIssuePermissionTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        self.qa_officer = User.objects.create_user(
            username='qaofficer1',
            password='Testpass123'
        )
        self.qa_officer.profile.role = Profile.ROLE_QA_OFFICER
        self.qa_officer.profile.save()

        self.issue = QualityIssue.objects.create(
            title='Permission test',
            description='Testing permissions.',
            issue_type=QualityIssue.TYPE_BUG,
            severity=QualityIssue.SEVERITY_MEDIUM,
            priority=QualityIssue.PRIORITY_MEDIUM,
            affected_system='Permission Module',
            reported_by=self.student,
        )

    def test_reporter_can_edit_submitted_issue(self):
        self.assertTrue(can_edit_issue(self.student, self.issue))

    def test_qa_officer_can_edit_issue(self):
        self.assertTrue(can_edit_issue(self.qa_officer, self.issue))

    def test_qa_officer_can_view_internal_comments(self):
        self.assertTrue(can_view_internal_comments(self.qa_officer))

    def test_student_cannot_view_internal_comments(self):
        self.assertFalse(can_view_internal_comments(self.student))


class QualityIssueViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        self.issue = QualityIssue.objects.create(
            title='View test issue',
            description='Testing views.',
            issue_type=QualityIssue.TYPE_BUG,
            severity=QualityIssue.SEVERITY_MEDIUM,
            priority=QualityIssue.PRIORITY_MEDIUM,
            affected_system='View Module',
            reported_by=self.user,
        )

    def test_issue_list_requires_login(self):
        response = self.client.get(reverse('quality:issue_list'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_issue_list(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.get(reverse('quality:issue_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quality Issues')

    def test_logged_in_user_can_view_issue_detail(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.get(
            reverse('quality:issue_detail', args=[self.issue.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View test issue')

    def test_logged_in_user_can_create_comment(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.post(
            reverse('quality:issue_detail', args=[self.issue.id]),
            {'comment': 'This is a test comment.', 'is_internal': False}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            IssueComment.objects.filter(comment='This is a test comment.').exists()
        )