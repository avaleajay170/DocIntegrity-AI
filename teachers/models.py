from django.db import models
from accounts.models import CustomUser


class TeacherProfile(models.Model):
    user        = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department  = models.CharField(max_length=100)
    phone       = models.CharField(max_length=15, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"


class Subject(models.Model):
    teacher    = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='subjects')
    name       = models.CharField(max_length=100)
    code       = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=20)
    division   = models.CharField(max_length=5, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"