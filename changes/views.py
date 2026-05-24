from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChangeCommentForm, ChangeRequestForm, ChangeRequestUpdateForm
from .models import ChangeRequest
from .services import (
    can_approve_change_request,
    can_edit_change_request,
    can_view_internal_comments,
    record_change_request_updates,
)


@login_required
def change_list(request):
    change_requests = ChangeRequest.objects.select_related(
        'requested_by',
        'assigned_to',
        'approved_by',
    )

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    risk_filter = request.GET.get('risk', '')

    if search_query:
        change_requests = change_requests.filter(
            Q(title__icontains=search_query)
            | Q(reason__icontains=search_query)
            | Q(proposed_change__icontains=search_query)
        )

    if status_filter:
        change_requests = change_requests.filter(status=status_filter)

    if type_filter:
        change_requests = change_requests.filter(change_type=type_filter)

    if risk_filter:
        change_requests = change_requests.filter(risk_level=risk_filter)

    context = {
        'change_requests': change_requests,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'risk_filter': risk_filter,
        'status_choices': ChangeRequest.STATUS_CHOICES,
        'type_choices': ChangeRequest.CHANGE_TYPE_CHOICES,
        'risk_choices': ChangeRequest.RISK_CHOICES,
    }

    return render(request, 'changes/change_list.html', context)


@login_required
def change_create(request):
    if request.method == 'POST':
        form = ChangeRequestForm(request.POST)

        if form.is_valid():
            change_request = form.save(commit=False)
            change_request.requested_by = request.user
            change_request.save()

            messages.success(request, 'Change request submitted successfully.')
            return redirect('changes:change_detail', change_id=change_request.id)

        messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangeRequestForm()

    return render(request, 'changes/change_form.html', {'form': form})


@login_required
def change_detail(request, change_id):
    change_request = get_object_or_404(
        ChangeRequest.objects.select_related(
            'requested_by',
            'assigned_to',
            'approved_by',
        ),
        id=change_id
    )

    if can_view_internal_comments(request.user):
        comments = change_request.comments.select_related('author')
    else:
        comments = change_request.comments.filter(
            is_internal=False
        ).select_related('author')

    history = change_request.history.select_related('changed_by')

    if request.method == 'POST':
        comment_form = ChangeCommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.change_request = change_request
            comment.author = request.user

            if comment.is_internal and not can_view_internal_comments(request.user):
                messages.error(request, 'You cannot create internal comments.')
                return redirect('changes:change_detail', change_id=change_request.id)

            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('changes:change_detail', change_id=change_request.id)

        messages.error(request, 'Comment cannot be empty.')
    else:
        comment_form = ChangeCommentForm()

    context = {
        'change_request': change_request,
        'comments': comments,
        'history': history,
        'comment_form': comment_form,
        'can_edit': can_edit_change_request(request.user, change_request),
        'can_approve': can_approve_change_request(request.user),
        'can_view_internal': can_view_internal_comments(request.user),
    }

    return render(request, 'changes/change_detail.html', context)


@login_required
def change_update(request, change_id):
    change_request = get_object_or_404(ChangeRequest, id=change_id)

    if not can_edit_change_request(request.user, change_request):
        messages.error(
            request,
            'You do not have permission to edit this change request.'
        )
        return redirect('changes:change_detail', change_id=change_request.id)

    if request.method == 'POST':
        form = ChangeRequestUpdateForm(request.POST, instance=change_request)

        if form.is_valid():
            updated_change = form.save(commit=False)
            record_change_request_updates(updated_change, form, request.user)
            updated_change.save()

            messages.success(request, 'Change request updated successfully.')
            return redirect('changes:change_detail', change_id=change_request.id)

        messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangeRequestUpdateForm(instance=change_request)

    return render(
        request,
        'changes/change_update_form.html',
        {
            'form': form,
            'change_request': change_request,
        }
    )


@login_required
def approve_change(request, change_id):
    change_request = get_object_or_404(ChangeRequest, id=change_id)

    if not can_approve_change_request(request.user):
        messages.error(
            request,
            'Only project managers and administrators can approve changes.'
        )
        return redirect('changes:change_detail', change_id=change_request.id)

    if change_request.status not in [
        ChangeRequest.STATUS_SUBMITTED,
        ChangeRequest.STATUS_UNDER_REVIEW,
    ]:
        messages.error(request, 'Only submitted or under-review changes can be approved.')
        return redirect('changes:change_detail', change_id=change_request.id)

    change_request.approve(request.user, 'Approved after impact assessment review.')

    messages.success(request, 'Change request approved successfully.')
    return redirect('changes:change_detail', change_id=change_request.id)


@login_required
def reject_change(request, change_id):
    change_request = get_object_or_404(ChangeRequest, id=change_id)

    if not can_approve_change_request(request.user):
        messages.error(
            request,
            'Only project managers and administrators can reject changes.'
        )
        return redirect('changes:change_detail', change_id=change_request.id)

    if change_request.status not in [
        ChangeRequest.STATUS_SUBMITTED,
        ChangeRequest.STATUS_UNDER_REVIEW,
    ]:
        messages.error(request, 'Only submitted or under-review changes can be rejected.')
        return redirect('changes:change_detail', change_id=change_request.id)

    change_request.reject(request.user, 'Rejected after impact assessment review.')

    messages.success(request, 'Change request rejected.')
    return redirect('changes:change_detail', change_id=change_request.id)


@login_required
def my_changes(request):
    change_requests = ChangeRequest.objects.filter(
        Q(requested_by=request.user) | Q(assigned_to=request.user)
    ).select_related('requested_by', 'assigned_to', 'approved_by')

    return render(
        request,
        'changes/my_changes.html',
        {'change_requests': change_requests}
    )