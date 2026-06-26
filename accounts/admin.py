from django.contrib import admin
# Teacher profiles visible in admin for OSS. Pro has dashboard for all teachers.
from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'phone_number', 'is_verified', 'verified_at', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'institution']
    readonly_fields = ['created_at', 'updated_at']

