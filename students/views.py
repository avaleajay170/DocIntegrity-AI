from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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


def get_student_profile(request):
    try:
        return StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return None


@student_required
def student_dashboard(request):
    profile         = get_student_profile(request)
    has_sample      = False
    assignments     = []
    pending_count   = 0
    submitted_count = 0
    flagged_count   = 0

    if profile:
        has_sample = HandwritingSample.objects.filter(
            student=profile, is_active=True
        ).exists()

        class_assignments = Assignment.objects.filter(
            subject__class_name=profile.class_name
        ).order_by('-created_at')

        for assignment in class_assignments:
            try:
                submission      = Submission.objects.get(assignment=assignment, student=profile)
                submitted       = True
                submitted_count += 1
                if submission.status == 'flagged':
                    flagged_count += 1
            except Submission.DoesNotExist:
                submission    = None
                submitted     = False
                pending_count += 1

            assignments.append({
                'assignment': assignment,
                'submitted':  submitted,
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
    profile     = get_student_profile(request)
    assignments = []

    if profile:
        class_assignments = Assignment.objects.filter(
            subject__class_name=profile.class_name
        ).order_by('-created_at')

        for assignment in class_assignments:
            try:
                submission = Submission.objects.get(assignment=assignment, student=profile)
                submitted  = True
            except Submission.DoesNotExist:
                submission = None
                submitted  = False

            assignments.append({
                'assignment': assignment,
                'submitted':  submitted,
                'submission': submission,
            })

    return render(request, 'students/assignments.html', {
        'assignments': assignments,
        'profile':     profile,
    })


@student_required
def student_submissions(request):
    profile     = get_student_profile(request)
    submissions = Submission.objects.filter(
        student=profile
    ).select_related(
        'assignment__subject', 'verification'
    ).order_by('-submitted_at') if profile else []

    return render(request, 'students/submissions.html', {
        'submissions': submissions,
        'profile':     profile,
    })


@student_required
def upload_sample(request):
    profile        = get_student_profile(request)
    current_sample = None

    if profile:
        current_sample = HandwritingSample.objects.filter(
            student=profile, is_active=True
        ).first()

    if request.method == 'POST':
        if not profile:
            messages.error(request, 'Student profile not found. Contact admin.')
            return redirect('upload_sample')

        image = request.FILES.get('image')
        if not image:
            messages.error(request, 'Please select an image.')
        else:
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if image.content_type not in allowed_types:
                messages.error(request, 'Only JPG and PNG images are supported for reference sample.')
            else:
                HandwritingSample.objects.create(
                    student=profile,
                    image=image,
                    is_active=True,
                )
                messages.success(request, 'Handwriting sample uploaded successfully.')
                return redirect('student_dashboard')

    return render(request, 'students/upload_sample.html', {
        'profile':        profile,
        'current_sample': current_sample,
    })


@student_required
def submit_assignment(request, assignment_id):
    profile    = get_student_profile(request)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if not profile:
        messages.error(request, 'Student profile not found. Contact admin.')
        return redirect('student_dashboard')

    # Check if already submitted
    if Submission.objects.filter(assignment=assignment, student=profile).exists():
        messages.error(request, 'You have already submitted this assignment.')
        return redirect('student_assignments')

    # Check if reference sample exists
    if not HandwritingSample.objects.filter(student=profile, is_active=True).exists():
        messages.error(request, 'Please upload your handwriting reference sample first.')
        return redirect('upload_sample')

    # Check deadline
    if timezone.now() > assignment.deadline:
        messages.error(request, 'Deadline has passed. You cannot submit this assignment.')
        return redirect('student_assignments')

    if request.method == 'POST':
        file = request.FILES.get('image')
        if not file:
            messages.error(request, 'Please select a file.')
        else:
            allowed_types = [
                'image/jpeg', 'image/png', 'image/jpg',
                'application/pdf'
            ]
            if file.content_type not in allowed_types:
                messages.error(request, 'Only JPG, PNG and PDF files are supported.')
            else:
                Submission.objects.create(
                    assignment=assignment,
                    student=profile,
                    image=file,
                    status='pending',
                )
                messages.success(request, 'Assignment submitted successfully.')
                return redirect('student_assignments')

    return render(request, 'students/submit_assignment.html', {
        'assignment': assignment,
        'profile':    profile,
    })


@student_required
def view_submission(request, submission_id):
    profile    = get_student_profile(request)
    submission = get_object_or_404(Submission, id=submission_id, student=profile)

    return render(request, 'students/view_submission.html', {
        'submission': submission,
        'profile':    profile,
    })