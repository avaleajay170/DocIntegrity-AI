from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StudentProfile, HandwritingSample
from assignments.models import Assignment, Submission


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'student':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@student_required
def student_dashboard(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        profile = None

    has_sample = False
    if profile:
        has_sample = HandwritingSample.objects.filter(
            student=profile, is_active=True
        ).exists()

    # Get assignments for student's class
    assignments = []
    pending_count = 0
    submitted_count = 0
    flagged_count = 0

    if profile:
        class_assignments = Assignment.objects.filter(
            subject__class_name=profile.class_name
        ).order_by('-created_at')

        for assignment in class_assignments:
            try:
                submission = Submission.objects.get(
                    assignment=assignment, student=profile
                )
                submitted = True
                if submission.status == 'flagged':
                    flagged_count += 1
                submitted_count += 1
            except Submission.DoesNotExist:
                submission = None
                submitted = False
                pending_count += 1

            assignments.append({
                'assignment': assignment,
                'submitted': submitted,
                'submission': submission,
            })

    return render(request, 'students/dashboard.html', {
        'profile':            profile,
        'has_sample':         has_sample,
        'recent_assignments': assignments[:5],
        'pending_count':      pending_count,
        'submitted_count':    submitted_count,
        'flagged_count':      flagged_count,
    })


@student_required
def student_assignments(request):
    return render(request, 'students/assignments.html')


@student_required
def student_submissions(request):
    return render(request, 'students/submissions.html')


@student_required
def upload_sample(request):
    return render(request, 'students/upload_sample.html')


@student_required
def submit_assignment(request, assignment_id):
    return render(request, 'students/submit_assignment.html')


@student_required
def view_submission(request, submission_id):
    return render(request, 'students/view_submission.html')