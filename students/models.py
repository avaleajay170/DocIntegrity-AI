from django.db import models
from accounts.models import CustomUser


class StudentProfile(models.Model):
    user        = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    class_name  = models.CharField(max_length=20)
    division    = models.CharField(max_length=5)
    phone       = models.CharField(max_length=15, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.roll_number})"


class HandwritingSample(models.Model):
    student     = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='samples')
    image       = models.ImageField(upload_to='samples/')
    is_active   = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    features_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Sample — {self.student.user.full_name} ({'Active' if self.is_active else 'Inactive'})"

    def save(self, *args, **kwargs):
        if self.is_active:
            HandwritingSample.objects.filter(
                student=self.student, is_active=True
            ).update(is_active=False)
        super().save(*args, **kwargs)