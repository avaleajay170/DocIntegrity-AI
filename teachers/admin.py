from django.contrib import admin
from .models import TeacherProfile, Subject


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'employee_id', 'department', 'created_at')
    search_fields = ('user__full_name', 'employee_id')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'teacher', 'class_name', 'division')
    search_fields = ('name', 'code')
    list_filter   = ('class_name',)