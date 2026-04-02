from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TeacherRegistrationForm, LoginForm


def register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('accounts:verify_otp')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('quiz:teacher_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('quiz:landing')


def verify_otp(request):
    return render(request, 'accounts/verify_otp.html')


def verify_email(request, uidb64, token):
    return render(request, 'accounts/email_confirm.html')


def resend_otp(request):
    return redirect('accounts:verify_otp')

