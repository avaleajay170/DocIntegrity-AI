from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                              views.student_dashboard,   name='student_dashboard'),
    path('assignments/',                            views.student_assignments, name='student_assignments'),
    path('submissions/',                            views.student_submissions, name='student_submissions'),
    path('sample/upload/',                          views.upload_sample,       name='upload_sample'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment,   name='submit_assignment'),
    path('submissions/<int:submission_id>/',        views.view_submission,     name='view_submission'),
]