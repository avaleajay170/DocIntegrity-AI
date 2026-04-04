from django.db import models
from assignments.models import Submission


class VerificationResult(models.Model):
    HW_VERDICT_CHOICES = [
        ('matched',   'Matched'),
        ('uncertain', 'Uncertain'),
        ('mismatch',  'Mismatch'),
    ]
    AI_VERDICT_CHOICES = [
        ('human',        'Human Written'),
        ('mixed',        'Mixed Content'),
        ('ai_generated', 'AI Generated'),
    ]

    submission       = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='verification')
    hw_match_score   = models.FloatField(default=0.0)
    ai_content_score = models.FloatField(default=0.0)
    hw_verdict       = models.CharField(max_length=20, choices=HW_VERDICT_CHOICES, default='uncertain')
    ai_verdict       = models.CharField(max_length=20, choices=AI_VERDICT_CHOICES, default='human')
    extracted_text   = models.TextField(blank=True)
    analysed_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result — {self.submission.student.user.full_name} | HW: {self.hw_match_score}% | AI: {self.ai_content_score}%"

    def set_hw_verdict(self):
        if self.hw_match_score >= 85:
            self.hw_verdict = 'matched'
        elif self.hw_match_score >= 50:
            self.hw_verdict = 'uncertain'
        else:
            self.hw_verdict = 'mismatch'

    def set_ai_verdict(self):
        if self.ai_content_score <= 20:
            self.ai_verdict = 'human'
        elif self.ai_content_score <= 60:
            self.ai_verdict = 'mixed'
        else:
            self.ai_verdict = 'ai_generated'