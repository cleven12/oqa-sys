from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]
