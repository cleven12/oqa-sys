from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import TeacherRegistrationForm, LoginForm
from .models import TeacherProfile


def register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-activate the user (skip OTP for now)
            user.is_active = True
            user.save()
            
            # Update teacher profile
            try:
                profile = user.teacher_profile
                profile.is_verified = True
                profile.verified_at = timezone.now()
                profile.save()
            except:
                pass
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('accounts:login')
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


@login_required
def profile(request):
    """View and edit teacher profile"""
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        # Create profile if it doesn't exist
        teacher_profile = TeacherProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile info
        teacher_profile.phone_number = request.POST.get('phone_number', '')
        teacher_profile.institution = request.POST.get('institution', '')
        teacher_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', {
        'teacher_profile': teacher_profile
    })


def verify_otp(request):
    return render(request, 'accounts/verify_otp.html')


def verify_email(request, uidb64, token):
    return render(request, 'accounts/email_confirm.html')


def resend_otp(request):
    return redirect('accounts:verify_otp')

