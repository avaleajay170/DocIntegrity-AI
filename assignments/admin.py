from django.contrib import admin
from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display  = ('title', 'subject', 'deadline', 'created_at')
    search_fields = ('title',)
    list_filter   = ('subject',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ('student', 'assignment', 'status', 'submitted_at')
    list_filter   = ('status',)
    search_fields = ('student__user__full_name',)