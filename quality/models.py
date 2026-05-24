from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class QualityIssue(models.Model):
    TYPE_BUG = 'bug'
    TYPE_INCIDENT = 'incident'
    TYPE_SECURITY = 'security'
    TYPE_NON_CONFORMANCE = 'non_conformance'
    TYPE_DOCUMENTATION = 'documentation'
    TYPE_TESTING_DEFECT = 'testing_defect'

    ISSUE_TYPE_CHOICES = [
        (TYPE_BUG, 'Bug'),
        (TYPE_INCIDENT, 'Service Incident'),
        (TYPE_SECURITY, 'Security Vulnerability'),
        (TYPE_NON_CONFORMANCE, 'Non-Conformance'),
        (TYPE_DOCUMENTATION, 'Documentation Issue'),
        (TYPE_TESTING_DEFECT, 'Testing Defect'),
    ]

    SEVERITY_LOW = 'low'
    SEVERITY_MEDIUM = 'medium'
    SEVERITY_HIGH = 'high'
    SEVERITY_CRITICAL = 'critical'

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, 'Low'),
        (SEVERITY_MEDIUM, 'Medium'),
        (SEVERITY_HIGH, 'High'),
        (SEVERITY_CRITICAL, 'Critical'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_ASSIGNED = 'assigned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_VERIFIED = 'verified'
    STATUS_CLOSED = 'closed'
    STATUS_REOPENED = 'reopened'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_REOPENED, 'Reopened'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPE_CHOICES)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_MEDIUM
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM
    )
    affected_system = models.CharField(max_length=150)
    expected_result = models.TextField(blank=True)
    actual_result = models.TextField(blank=True)
    steps_to_reproduce = models.TextField(blank=True)
    attachment = models.FileField(upload_to='issue_attachments/', blank=True, null=True)

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_issues'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_issues',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )

    due_date = models.DateField(blank=True, null=True)
    resolution_summary = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        if not self.due_date:
            return False

        return self.due_date < timezone.now().date() and self.status not in [
            self.STATUS_CLOSED,
            self.STATUS_RESOLVED,
            self.STATUS_VERIFIED,
        ]

    def mark_resolved(self, summary):
        self.status = self.STATUS_RESOLVED
        self.resolution_summary = summary
        self.resolved_at = timezone.now()
        self.save()

    def close_issue(self):
        self.status = self.STATUS_CLOSED
        self.closed_at = timezone.now()
        self.save()


class IssueComment(models.Model):
    issue = models.ForeignKey(
        QualityIssue,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"


class IssueHistory(models.Model):
    issue = models.ForeignKey(
        QualityIssue,
        on_delete=models.CASCADE,
        related_name='history'
    )
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_name = models.CharField(max_length=100)
    old_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)
    change_note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.field_name} changed on {self.issue.title}"