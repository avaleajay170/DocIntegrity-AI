from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    error = None
    role  = request.POST.get('role', 'student')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=email, password=password)

        if user is not None:
            if user.role == role:
                login(request, user)
                return redirect_by_role(user)
            else:
                error = f'This account is not registered as a {role}.'
        else:
            error = 'Invalid email or password.'

    return render(request, 'accounts/login.html', {'error': error, 'role': role})


def redirect_by_role(user):
    if user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('/admin/')


def logout_view(request):
    logout(request)
    return redirect('login')