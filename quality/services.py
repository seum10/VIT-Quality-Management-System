from .models import IssueHistory


def create_issue_history(issue, changed_by, field_name, old_value, new_value, note=''):
    return IssueHistory.objects.create(
        issue=issue,
        changed_by=changed_by,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else '',
        new_value=str(new_value) if new_value is not None else '',
        change_note=note,
    )


def record_issue_changes(issue, form, changed_by):
    if not form.changed_data:
        return

    for field_name in form.changed_data:
        old_value = form.initial.get(field_name, '')
        new_value = form.cleaned_data.get(field_name, '')

        create_issue_history(
            issue=issue,
            changed_by=changed_by,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            note=f'{field_name} was updated.'
        )


def can_edit_issue(user, issue):
    if not user.is_authenticated:
        return False

    user_role = getattr(user.profile, 'role', None)

    if user == issue.reported_by and issue.status in [
        issue.STATUS_SUBMITTED,
        issue.STATUS_REOPENED,
    ]:
        return True

    if user_role in ['qa_officer', 'developer', 'project_manager', 'admin']:
        return True

    return False


def can_view_internal_comments(user):
    if not user.is_authenticated:
        return False

    user_role = getattr(user.profile, 'role', None)

    return user_role in ['qa_officer', 'developer', 'project_manager', 'admin']