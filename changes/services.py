from .models import ChangeHistory


def create_change_history(
    change_request,
    changed_by,
    field_name,
    old_value,
    new_value,
    note=''
):
    return ChangeHistory.objects.create(
        change_request=change_request,
        changed_by=changed_by,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else '',
        new_value=str(new_value) if new_value is not None else '',
        change_note=note,
    )


def record_change_request_updates(change_request, form, changed_by):
    if not form.changed_data:
        return

    for field_name in form.changed_data:
        old_value = form.initial.get(field_name, '')
        new_value = form.cleaned_data.get(field_name, '')

        create_change_history(
            change_request=change_request,
            changed_by=changed_by,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            note=f'{field_name} was updated.'
        )


def can_edit_change_request(user, change_request):
    if not user.is_authenticated:
        return False

    user_role = getattr(user.profile, 'role', None)

    if user == change_request.requested_by and change_request.status in [
        change_request.STATUS_DRAFT,
        change_request.STATUS_SUBMITTED,
    ]:
        return True

    return user_role in [
        'qa_officer',
        'developer',
        'project_manager',
        'admin',
    ]


def can_approve_change_request(user):
    if not user.is_authenticated:
        return False

    user_role = getattr(user.profile, 'role', None)

    return user_role in ['project_manager', 'admin']


def can_view_internal_comments(user):
    if not user.is_authenticated:
        return False

    user_role = getattr(user.profile, 'role', None)

    return user_role in [
        'qa_officer',
        'developer',
        'project_manager',
        'admin',
    ]