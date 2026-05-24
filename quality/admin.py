from django.contrib import admin

from .models import IssueComment, IssueHistory, QualityIssue


class IssueCommentInline(admin.TabularInline):
    model = IssueComment
    extra = 0


class IssueHistoryInline(admin.TabularInline):
    model = IssueHistory
    extra = 0
    readonly_fields = [
        'changed_by',
        'field_name',
        'old_value',
        'new_value',
        'change_note',
        'changed_at',
    ]


@admin.register(QualityIssue)
class QualityIssueAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'issue_type',
        'severity',
        'priority',
        'status',
        'reported_by',
        'assigned_to',
        'created_at',
    ]
    list_filter = ['issue_type', 'severity', 'priority', 'status']
    search_fields = ['title', 'description', 'affected_system']
    inlines = [IssueCommentInline, IssueHistoryInline]


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ['issue', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal']


@admin.register(IssueHistory)
class IssueHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'issue',
        'changed_by',
        'field_name',
        'old_value',
        'new_value',
        'changed_at',
    ]
    list_filter = ['field_name', 'changed_at']