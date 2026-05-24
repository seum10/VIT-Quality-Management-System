from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IssueCommentForm, QualityIssueForm, QualityIssueUpdateForm
from .models import QualityIssue
from .services import can_edit_issue, can_view_internal_comments, record_issue_changes


@login_required
def issue_list(request):
    issues = QualityIssue.objects.select_related(
        'reported_by',
        'assigned_to',
    )

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    severity_filter = request.GET.get('severity', '')

    if search_query:
        issues = issues.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(affected_system__icontains=search_query)
        )

    if status_filter:
        issues = issues.filter(status=status_filter)

    if type_filter:
        issues = issues.filter(issue_type=type_filter)

    if severity_filter:
        issues = issues.filter(severity=severity_filter)

    context = {
        'issues': issues,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'severity_filter': severity_filter,
        'status_choices': QualityIssue.STATUS_CHOICES,
        'type_choices': QualityIssue.ISSUE_TYPE_CHOICES,
        'severity_choices': QualityIssue.SEVERITY_CHOICES,
    }

    return render(request, 'quality/issue_list.html', context)


@login_required
def issue_create(request):
    if request.method == 'POST':
        form = QualityIssueForm(request.POST, request.FILES)

        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user
            issue.save()

            messages.success(request, 'Quality issue submitted successfully.')
            return redirect('quality:issue_detail', issue_id=issue.id)

        messages.error(request, 'Please correct the errors below.')
    else:
        form = QualityIssueForm()

    return render(request, 'quality/issue_form.html', {'form': form})


@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(
        QualityIssue.objects.select_related('reported_by', 'assigned_to'),
        id=issue_id
    )

    if can_view_internal_comments(request.user):
        comments = issue.comments.select_related('author')
    else:
        comments = issue.comments.filter(is_internal=False).select_related('author')

    history = issue.history.select_related('changed_by')

    if request.method == 'POST':
        comment_form = IssueCommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.issue = issue
            comment.author = request.user

            if comment.is_internal and not can_view_internal_comments(request.user):
                messages.error(request, 'You cannot create internal comments.')
                return redirect('quality:issue_detail', issue_id=issue.id)

            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('quality:issue_detail', issue_id=issue.id)

        messages.error(request, 'Comment cannot be empty.')
    else:
        comment_form = IssueCommentForm()

    context = {
        'issue': issue,
        'comments': comments,
        'history': history,
        'comment_form': comment_form,
        'can_edit': can_edit_issue(request.user, issue),
        'can_view_internal': can_view_internal_comments(request.user),
    }

    return render(request, 'quality/issue_detail.html', context)


@login_required
def issue_update(request, issue_id):
    issue = get_object_or_404(QualityIssue, id=issue_id)

    if not can_edit_issue(request.user, issue):
        messages.error(request, 'You do not have permission to edit this issue.')
        return redirect('quality:issue_detail', issue_id=issue.id)

    if request.method == 'POST':
        form = QualityIssueUpdateForm(request.POST, instance=issue)

        if form.is_valid():
            updated_issue = form.save(commit=False)
            record_issue_changes(updated_issue, form, request.user)
            updated_issue.save()

            messages.success(request, 'Quality issue updated successfully.')
            return redirect('quality:issue_detail', issue_id=issue.id)

        messages.error(request, 'Please correct the errors below.')
    else:
        form = QualityIssueUpdateForm(instance=issue)

    return render(
        request,
        'quality/issue_update_form.html',
        {
            'form': form,
            'issue': issue,
        }
    )


@login_required
def my_issues(request):
    issues = QualityIssue.objects.filter(
        Q(reported_by=request.user) | Q(assigned_to=request.user)
    ).select_related('reported_by', 'assigned_to')

    return render(request, 'quality/my_issues.html', {'issues': issues})