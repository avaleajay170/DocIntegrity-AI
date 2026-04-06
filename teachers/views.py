from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import TeacherProfile, Subject
from assignments.models import Assignment, Submission


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'teacher':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_teacher_profile(request):
    try:
        return TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        return None


@teacher_required
def teacher_dashboard(request):
    profile = get_teacher_profile(request)

    submissions = Submission.objects.filter(
        assignment__subject__teacher=profile
    ).select_related(
        'student__user', 'assignment__subject', 'verification'
    ).order_by('-submitted_at') if profile else []

    total_submissions    = len(submissions)
    pending_verification = sum(1 for s in submissions if s.status == 'pending')
    flagged_count        = sum(1 for s in submissions if s.status == 'flagged')
    verified_count       = sum(1 for s in submissions if s.status == 'verified')

    return render(request, 'teachers/dashboard.html', {
        'profile':              profile,
        'recent_submissions':   list(submissions)[:10],
        'total_submissions':    total_submissions,
        'pending_verification': pending_verification,
        'flagged_count':        flagged_count,
        'verified_count':       verified_count,
    })


@teacher_required
def teacher_subjects(request):
    profile  = get_teacher_profile(request)
    subjects = Subject.objects.filter(teacher=profile) if profile else []
    return render(request, 'teachers/subjects.html', {
        'subjects': subjects,
        'profile':  profile,
    })


@teacher_required
def create_subject(request):
    profile = get_teacher_profile(request)
    if request.method == 'POST':
        name       = request.POST.get('name', '').strip()
        code       = request.POST.get('code', '').strip()
        class_name = request.POST.get('class_name', '').strip()
        division   = request.POST.get('division', '').strip()

        if not name or not code or not class_name:
            messages.error(request, 'Please fill all required fields.')
        elif Subject.objects.filter(code=code).exists():
            messages.error(request, f'Subject code {code} already exists.')
        else:
            Subject.objects.create(
                teacher=profile,
                name=name,
                code=code,
                class_name=class_name,
                division=division,
            )
            messages.success(request, f'Subject "{name}" created successfully.')
            return redirect('teacher_subjects')

    return render(request, 'teachers/create_subject.html', {'profile': profile})


@teacher_required
def teacher_assignments(request):
    profile     = get_teacher_profile(request)
    assignments = Assignment.objects.filter(
        subject__teacher=profile
    ).select_related('subject').order_by('-created_at') if profile else []
    return render(request, 'teachers/assignments.html', {
        'assignments': assignments,
        'profile':     profile,
    })


@teacher_required
def create_assignment(request):
    profile  = get_teacher_profile(request)
    subjects = Subject.objects.filter(teacher=profile) if profile else []

    if request.method == 'POST':
        subject_id  = request.POST.get('subject')
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        deadline    = request.POST.get('deadline', '').strip()

        if not subject_id or not title or not deadline:
            messages.error(request, 'Please fill all required fields.')
        else:
            subject = get_object_or_404(Subject, id=subject_id, teacher=profile)
            Assignment.objects.create(
                subject=subject,
                title=title,
                description=description,
                deadline=deadline,
            )
            messages.success(request, f'Assignment "{title}" created successfully.')
            return redirect('teacher_assignments')

    return render(request, 'teachers/create_assignment.html', {
        'subjects': subjects,
        'profile':  profile,
    })


@teacher_required
def teacher_submissions(request):
    profile     = get_teacher_profile(request)
    submissions = Submission.objects.filter(
        assignment__subject__teacher=profile
    ).select_related(
        'student__user', 'assignment__subject', 'verification'
    ).order_by('-submitted_at') if profile else []

    status_filter = request.GET.get('status', '')
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    return render(request, 'teachers/submissions.html', {
        'submissions':    submissions,
        'status_filter':  status_filter,
        'profile':        profile,
    })


@teacher_required
def flagged_submissions(request):
    profile     = get_teacher_profile(request)
    submissions = Submission.objects.filter(
        assignment__subject__teacher=profile,
        status='flagged'
    ).select_related(
        'student__user', 'assignment__subject', 'verification'
    ).order_by('-submitted_at') if profile else []

    return render(request, 'teachers/flagged.html', {
        'submissions': submissions,
        'profile':     profile,
    })


@teacher_required
def review_submission(request, submission_id):
    profile    = get_teacher_profile(request)
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        assignment__subject__teacher=profile
    )

    if request.method == 'POST':
        status = request.POST.get('status')
        remark = request.POST.get('remark', '').strip()
        if status in ['verified', 'flagged', 'rejected']:
            submission.status         = status
            submission.teacher_remark = remark
            submission.save()
            messages.success(request, f'Submission marked as {status}.')
            return redirect('teacher_submissions')

    return render(request, 'teachers/review_submission.html', {
        'submission': submission,
        'profile':    profile,
    })