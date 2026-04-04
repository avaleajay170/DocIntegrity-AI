from django.contrib import admin
from .models import VerificationResult


@admin.register(VerificationResult)
class VerificationResultAdmin(admin.ModelAdmin):
    list_display  = ('submission', 'hw_match_score', 'ai_content_score', 'hw_verdict', 'ai_verdict', 'analysed_at')
    list_filter   = ('hw_verdict', 'ai_verdict')
    search_fields = ('submission__student__user__full_name',)