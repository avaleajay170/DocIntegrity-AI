from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                          views.teacher_dashboard,   name='teacher_dashboard'),
    path('subjects/',                           views.teacher_subjects,    name='teacher_subjects'),
    path('assignments/',                        views.teacher_assignments, name='teacher_assignments'),
    path('assignments/create/',                 views.create_assignment,   name='create_assignment'),
    path('submissions/',                        views.teacher_submissions, name='teacher_submissions'),
    path('submissions/<int:submission_id>/review/', views.review_submission, name='review_submission'),
    path('flagged/',                            views.flagged_submissions,  name='flagged_submissions'),
]