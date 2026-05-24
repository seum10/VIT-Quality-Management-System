from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ChangeRequest(models.Model):
    TYPE_FEATURE = 'feature'
    TYPE_BUG_FIX = 'bug_fix'
    TYPE_SECURITY_FIX = 'security_fix'
    TYPE_CONFIGURATION = 'configuration'
    TYPE_DOCUMENTATION = 'documentation'
    TYPE_PROCESS = 'process'

    CHANGE_TYPE_CHOICES = [
        (TYPE_FEATURE, 'New Feature'),
        (TYPE_BUG_FIX, 'Bug Fix'),
        (TYPE_SECURITY_FIX, 'Security Fix'),
        (TYPE_CONFIGURATION, 'Configuration Change'),
        (TYPE_DOCUMENTATION, 'Documentation Change'),
        (TYPE_PROCESS, 'Process Change'),
    ]

    RISK_LOW = 'low'
    RISK_MEDIUM = 'medium'
    RISK_HIGH = 'high'
    RISK_CRITICAL = 'critical'

    RISK_CHOICES = [
        (RISK_LOW, 'Low'),
        (RISK_MEDIUM, 'Medium'),
        (RISK_HIGH, 'High'),
        (RISK_CRITICAL, 'Critical'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_IMPLEMENTED = 'implemented'
    STATUS_TESTED = 'tested'
    STATUS_RELEASED = 'released'
    STATUS_ROLLED_BACK = 'rolled_back'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_IMPLEMENTED, 'Implemented'),
        (STATUS_TESTED, 'Tested'),
        (STATUS_RELEASED, 'Released'),
        (STATUS_ROLLED_BACK, 'Rolled Back'),
        (STATUS_CLOSED, 'Closed'),
    ]

    title = models.CharField(max_length=200)
    change_type = models.CharField(max_length=30, choices=CHANGE_TYPE_CHOICES)
    reason = models.TextField()
    current_state = models.TextField()
    proposed_change = models.TextField()

    business_impact = models.TextField()
    technical_impact = models.TextField()
    security_impact = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_CHOICES,
        default=RISK_MEDIUM
    )

    implementation_plan = models.TextField()
    testing_plan = models.TextField()
    rollback_plan = models.TextField()

    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_changes'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_changes',
        blank=True,
        null=True
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='approved_changes',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )

    target_release_date = models.DateField(blank=True, null=True)
    approval_notes = models.TextField(blank=True)
    implementation_notes = models.TextField(blank=True)
    testing_notes = models.TextField(blank=True)
    closure_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    released_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_high_risk(self):
        return self.risk_level in [self.RISK_HIGH, self.RISK_CRITICAL]

    @property
    def is_overdue(self):
        if not self.target_release_date:
            return False

        closed_statuses = [
            self.STATUS_RELEASED,
            self.STATUS_CLOSED,
            self.STATUS_REJECTED,
            self.STATUS_ROLLED_BACK,
        ]

        return (
            self.target_release_date < timezone.now().date()
            and self.status not in closed_statuses
        )

    def approve(self, user, notes=''):
        self.status = self.STATUS_APPROVED
        self.approved_by = user
        self.approval_notes = notes
        self.approved_at = timezone.now()
        self.save()

    def reject(self, user, notes=''):
        self.status = self.STATUS_REJECTED
        self.approved_by = user
        self.approval_notes = notes
        self.save()

    def close(self, notes=''):
        self.status = self.STATUS_CLOSED
        self.closure_notes = notes
        self.closed_at = timezone.now()
        self.save()


class ChangeComment(models.Model):
    change_request = models.ForeignKey(
        ChangeRequest,
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
        return f"Comment by {self.author.username} on {self.change_request.title}"


class ChangeHistory(models.Model):
    change_request = models.ForeignKey(
        ChangeRequest,
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
        return f"{self.field_name} changed on {self.change_request.title}"