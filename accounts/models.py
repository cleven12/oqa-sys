from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TeacherProfile(models.Model):
    """
    Extends Django User model for teacher-specific data.
    Linked to django-allauth for OTP and email verification.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.institution or 'No Institution'}"

    class Meta:
        db_table = 'teacher_profile'
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
