# Pro freelancer note: This auth is intentionally simple for easy OSS self-hosting.
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
            # Auto-activate the user (simplified auth for OSS ease of use)
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
            
            # Auto login for convenience
            login(request, user)
            messages.success(request, 'Registration successful! Welcome.')
            return redirect('quiz:teacher_dashboard')
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
            login_id = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            
            # Support login with email or username
            user = authenticate(request, username=login_id, password=password)
            if user is None:
                # Try email lookup
                from django.contrib.auth.models import User
                try:
                    user_obj = User.objects.get(email__iexact=login_id)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('quiz:teacher_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password')
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
    
    # Calculate statistics
    from quiz.models import Quiz, StudentSession
    total_quizzes = Quiz.objects.filter(created_by=request.user).count()
    active_quizzes = Quiz.objects.filter(created_by=request.user, is_active=True).count()
    total_students = StudentSession.objects.filter(quiz__created_by=request.user).values('reg_number').distinct().count()
    
    return render(request, 'accounts/profile.html', {
        'teacher_profile': teacher_profile,
        'total_quizzes': total_quizzes,
        'active_quizzes': active_quizzes,
        'total_students': total_students,
    })


def verify_otp(request):
    # Placeholder - full OTP flow disabled for simpler OSS self-host deployment.
    # Teachers use password-based auth after registration. Strong passwords recommended.
    messages.info(request, 'Email/OTP verification is not required in this build. Use your password to login.')
    return redirect('accounts:login')


def verify_email(request, uidb64, token):
    messages.info(request, 'Email verification not active. Please login with your credentials.')
    return redirect('accounts:login')


def resend_otp(request):
    return redirect('accounts:login')

