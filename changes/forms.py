from django import forms
from django.contrib.auth.models import User

from .models import ChangeComment, ChangeRequest


class ChangeRequestForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = [
            'title',
            'change_type',
            'reason',
            'current_state',
            'proposed_change',
            'business_impact',
            'technical_impact',
            'security_impact',
            'risk_level',
            'implementation_plan',
            'testing_plan',
            'rollback_plan',
            'target_release_date',
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'current_state': forms.Textarea(attrs={'rows': 3}),
            'proposed_change': forms.Textarea(attrs={'rows': 3}),
            'business_impact': forms.Textarea(attrs={'rows': 3}),
            'technical_impact': forms.Textarea(attrs={'rows': 3}),
            'security_impact': forms.Textarea(attrs={'rows': 3}),
            'implementation_plan': forms.Textarea(attrs={'rows': 3}),
            'testing_plan': forms.Textarea(attrs={'rows': 3}),
            'rollback_plan': forms.Textarea(attrs={'rows': 3}),
            'target_release_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['change_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['risk_level'].widget.attrs.update({'class': 'form-select'})


class ChangeRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = [
            'title',
            'change_type',
            'reason',
            'current_state',
            'proposed_change',
            'business_impact',
            'technical_impact',
            'security_impact',
            'risk_level',
            'implementation_plan',
            'testing_plan',
            'rollback_plan',
            'assigned_to',
            'status',
            'target_release_date',
            'approval_notes',
            'implementation_notes',
            'testing_notes',
            'closure_notes',
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'current_state': forms.Textarea(attrs={'rows': 3}),
            'proposed_change': forms.Textarea(attrs={'rows': 3}),
            'business_impact': forms.Textarea(attrs={'rows': 3}),
            'technical_impact': forms.Textarea(attrs={'rows': 3}),
            'security_impact': forms.Textarea(attrs={'rows': 3}),
            'implementation_plan': forms.Textarea(attrs={'rows': 3}),
            'testing_plan': forms.Textarea(attrs={'rows': 3}),
            'rollback_plan': forms.Textarea(attrs={'rows': 3}),
            'approval_notes': forms.Textarea(attrs={'rows': 3}),
            'implementation_notes': forms.Textarea(attrs={'rows': 3}),
            'testing_notes': forms.Textarea(attrs={'rows': 3}),
            'closure_notes': forms.Textarea(attrs={'rows': 3}),
            'target_release_date': forms.DateInput(attrs={'type': 'date'}),
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
            'change_type',
            'risk_level',
            'assigned_to',
            'status',
        ]

        for field_name in select_fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-select'})


class ChangeCommentForm(forms.ModelForm):
    class Meta:
        model = ChangeComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['comment'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_internal'].widget.attrs.update({'class': 'form-check-input'})