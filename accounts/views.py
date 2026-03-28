from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def register(request):
    return render(request, 'accounts/register.html')


def login_view(request):
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('quiz:landing')


def verify_otp(request):
    return render(request, 'accounts/verify_otp.html')


def verify_email(request, uidb64, token):
    return render(request, 'accounts/email_confirm.html')


def resend_otp(request):
    return redirect('accounts:verify_otp')

