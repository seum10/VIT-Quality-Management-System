from collections import Counter

from changes.models import ChangeRequest
from quality.models import QualityIssue


def get_quality_issue_metrics():
    issues = QualityIssue.objects.all()

    total_issues = issues.count()
    open_issues = issues.exclude(
        status__in=[
            QualityIssue.STATUS_RESOLVED,
            QualityIssue.STATUS_VERIFIED,
            QualityIssue.STATUS_CLOSED,
            QualityIssue.STATUS_REJECTED,
        ]
    ).count()

    resolved_issues = issues.filter(
        status__in=[
            QualityIssue.STATUS_RESOLVED,
            QualityIssue.STATUS_VERIFIED,
            QualityIssue.STATUS_CLOSED,
        ]
    ).count()

    critical_issues = issues.filter(
        severity=QualityIssue.SEVERITY_CRITICAL
    ).count()

    security_issues = issues.filter(
        issue_type=QualityIssue.TYPE_SECURITY
    ).count()

    overdue_issues = sum(1 for issue in issues if issue.is_overdue)

    return {
        'total_issues': total_issues,
        'open_issues': open_issues,
        'resolved_issues': resolved_issues,
        'critical_issues': critical_issues,
        'security_issues': security_issues,
        'overdue_issues': overdue_issues,
    }


def get_change_request_metrics():
    change_requests = ChangeRequest.objects.all()

    total_changes = change_requests.count()
    pending_changes = change_requests.filter(
        status__in=[
            ChangeRequest.STATUS_SUBMITTED,
            ChangeRequest.STATUS_UNDER_REVIEW,
        ]
    ).count()

    approved_changes = change_requests.filter(
        status=ChangeRequest.STATUS_APPROVED
    ).count()

    released_changes = change_requests.filter(
        status=ChangeRequest.STATUS_RELEASED
    ).count()

    high_risk_changes = change_requests.filter(
        risk_level__in=[
            ChangeRequest.RISK_HIGH,
            ChangeRequest.RISK_CRITICAL,
        ]
    ).count()

    overdue_changes = sum(
        1 for change_request in change_requests if change_request.is_overdue
    )

    return {
        'total_changes': total_changes,
        'pending_changes': pending_changes,
        'approved_changes': approved_changes,
        'released_changes': released_changes,
        'high_risk_changes': high_risk_changes,
        'overdue_changes': overdue_changes,
    }


def get_chart_data():
    issues = QualityIssue.objects.all()
    change_requests = ChangeRequest.objects.all()

    issue_status_counter = Counter(
        issue.get_status_display() for issue in issues
    )
    issue_severity_counter = Counter(
        issue.get_severity_display() for issue in issues
    )
    issue_type_counter = Counter(
        issue.get_issue_type_display() for issue in issues
    )
    change_risk_counter = Counter(
        change_request.get_risk_level_display() for change_request in change_requests
    )
    change_status_counter = Counter(
        change_request.get_status_display() for change_request in change_requests
    )

    return {
        'issue_status_labels': list(issue_status_counter.keys()),
        'issue_status_values': list(issue_status_counter.values()),

        'issue_severity_labels': list(issue_severity_counter.keys()),
        'issue_severity_values': list(issue_severity_counter.values()),

        'issue_type_labels': list(issue_type_counter.keys()),
        'issue_type_values': list(issue_type_counter.values()),

        'change_risk_labels': list(change_risk_counter.keys()),
        'change_risk_values': list(change_risk_counter.values()),

        'change_status_labels': list(change_status_counter.keys()),
        'change_status_values': list(change_status_counter.values()),
    }


def get_recent_records():
    recent_issues = QualityIssue.objects.select_related(
        'reported_by',
        'assigned_to',
    )[:5]

    recent_changes = ChangeRequest.objects.select_related(
        'requested_by',
        'assigned_to',
        'approved_by',
    )[:5]

    return {
        'recent_issues': recent_issues,
        'recent_changes': recent_changes,
    }