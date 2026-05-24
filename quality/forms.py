from django import forms
from django.contrib.auth.models import User

from .models import IssueComment, QualityIssue


class QualityIssueForm(forms.ModelForm):
    class Meta:
        model = QualityIssue
        fields = [
            'title',
            'description',
            'issue_type',
            'severity',
            'priority',
            'affected_system',
            'expected_result',
            'actual_result',
            'steps_to_reproduce',
            'attachment',
            'due_date',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'expected_result': forms.Textarea(attrs={'rows': 3}),
            'actual_result': forms.Textarea(attrs={'rows': 3}),
            'steps_to_reproduce': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        select_fields = ['issue_type', 'severity', 'priority']
        for field_name in select_fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-select'})


class QualityIssueUpdateForm(forms.ModelForm):
    class Meta:
        model = QualityIssue
        fields = [
            'title',
            'description',
            'issue_type',
            'severity',
            'priority',
            'affected_system',
            'expected_result',
            'actual_result',
            'steps_to_reproduce',
            'assigned_to',
            'status',
            'due_date',
            'resolution_summary',
            'verification_notes',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'expected_result': forms.Textarea(attrs={'rows': 3}),
            'actual_result': forms.Textarea(attrs={'rows': 3}),
            'steps_to_reproduce': forms.Textarea(attrs={'rows': 3}),
            'resolution_summary': forms.Textarea(attrs={'rows': 3}),
            'verification_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = User.objects.filter(
            profile__role__in=[
                'qa_officer',
                'developer',
                'project_manager',
                'admin',
            ]
        )

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        select_fields = [
            'issue_type',
            'severity',
            'priority',
            'assigned_to',
            'status',
        ]

        for field_name in select_fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-select'})


class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['comment'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_internal'].widget.attrs.update({'class': 'form-check-input'})