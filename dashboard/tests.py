from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from changes.models import ChangeRequest
from quality.models import QualityIssue
from .services import (
    get_change_request_metrics,
    get_chart_data,
    get_quality_issue_metrics,
)


class DashboardServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        QualityIssue.objects.create(
            title='Critical security issue',
            description='Security issue for dashboard test.',
            issue_type=QualityIssue.TYPE_SECURITY,
            severity=QualityIssue.SEVERITY_CRITICAL,
            priority=QualityIssue.PRIORITY_URGENT,
            affected_system='Security Module',
            reported_by=self.user,
        )

        ChangeRequest.objects.create(
            title='High risk security change',
            change_type=ChangeRequest.TYPE_SECURITY_FIX,
            reason='Fix security weakness.',
            current_state='Weak control.',
            proposed_change='Add strict permission.',
            business_impact='Improves compliance.',
            technical_impact='Updates access logic.',
            risk_level=ChangeRequest.RISK_HIGH,
            implementation_plan='Update permission service.',
            testing_plan='Run permission tests.',
            rollback_plan='Revert permission update.',
            requested_by=self.user,
        )

    def test_quality_issue_metrics(self):
        metrics = get_quality_issue_metrics()

        self.assertEqual(metrics['total_issues'], 1)
        self.assertEqual(metrics['critical_issues'], 1)
        self.assertEqual(metrics['security_issues'], 1)

    def test_change_request_metrics(self):
        metrics = get_change_request_metrics()

        self.assertEqual(metrics['total_changes'], 1)
        self.assertEqual(metrics['high_risk_changes'], 1)

    def test_chart_data_contains_labels_and_values(self):
        chart_data = get_chart_data()

        self.assertIn('issue_status_labels', chart_data)
        self.assertIn('change_risk_values', chart_data)


class DashboardViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_dashboard(self):
        self.client.login(username='student1', password='Testpass123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'VIT Quality Management Dashboard')