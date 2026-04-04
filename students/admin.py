from django.contrib import admin
from .models import StudentProfile, HandwritingSample


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'roll_number', 'class_name', 'division', 'created_at')
    search_fields = ('user__full_name', 'roll_number')
    list_filter   = ('class_name', 'division')


@admin.register(HandwritingSample)
class HandwritingSampleAdmin(admin.ModelAdmin):
    list_display  = ('student', 'is_active', 'uploaded_at')
    list_filter   = ('is_active',)