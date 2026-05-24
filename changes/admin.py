from django.contrib import admin

from .models import ChangeComment, ChangeHistory, ChangeRequest


class ChangeCommentInline(admin.TabularInline):
    model = ChangeComment
    extra = 0


class ChangeHistoryInline(admin.TabularInline):
    model = ChangeHistory
    extra = 0
    readonly_fields = [
        'changed_by',
        'field_name',
        'old_value',
        'new_value',
        'change_note',
        'changed_at',
    ]


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'change_type',
        'risk_level',
        'status',
        'requested_by',
        'assigned_to',
        'approved_by',
        'created_at',
    ]
    list_filter = ['change_type', 'risk_level', 'status']
    search_fields = ['title', 'reason', 'proposed_change']
    inlines = [ChangeCommentInline, ChangeHistoryInline]


@admin.register(ChangeComment)
class ChangeCommentAdmin(admin.ModelAdmin):
    list_display = ['change_request', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal']


@admin.register(ChangeHistory)
class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'change_request',
        'changed_by',
        'field_name',
        'old_value',
        'new_value',
        'changed_at',
    ]
    list_filter = ['field_name', 'changed_at']