from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TeacherProfile
from assignments.models import Assignment, Submission


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'teacher':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@teacher_required
def teacher_dashboard(request):
    try:
        profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        profile = None

    submissions = Submission.objects.filter(
        assignment__subject__teacher=profile
    ).select_related(
        'student__user', 'assignment__subject', 'verification'
    ).order_by('-submitted_at') if profile else []

    total_submissions   = len(submissions)
    pending_verification = sum(1 for s in submissions if s.status == 'pending')
    flagged_count       = sum(1 for s in submissions if s.status == 'flagged')
    verified_count      = sum(1 for s in submissions if s.status == 'verified')

    return render(request, 'teachers/dashboard.html', {
        'profile':             profile,
        'recent_submissions':  list(submissions)[:10],
        'total_submissions':   total_submissions,
        'pending_verification':pending_verification,
        'flagged_count':       flagged_count,
        'verified_count':      verified_count,
    })


@teacher_required
def teacher_subjects(request):
    return render(request, 'teachers/subjects.html')


@teacher_required
def teacher_assignments(request):
    return render(request, 'teachers/assignments.html')


@teacher_required
def teacher_submissions(request):
    return render(request, 'teachers/submissions.html')


@teacher_required
def flagged_submissions(request):
    return render(request, 'teachers/flagged.html')


@teacher_required
def create_assignment(request):
    return render(request, 'teachers/create_assignment.html')


@teacher_required
def review_submission(request, submission_id):
    return render(request, 'teachers/review_submission.html')