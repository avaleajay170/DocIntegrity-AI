from django.db import models
from students.models import StudentProfile
from teachers.models import Subject


class Assignment(models.Model):
    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline    = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.subject.name}"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('verified', 'Verified'),
        ('flagged',  'Flagged'),
        ('rejected', 'Rejected'),
    ]
    assignment     = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student        = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    image          = models.ImageField(upload_to='submissions/')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    teacher_remark = models.TextField(blank=True)
    submitted_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.user.full_name} — {self.assignment.title} ({self.status})"