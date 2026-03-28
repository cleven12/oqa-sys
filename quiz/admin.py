from django.contrib import admin
from .models import Quiz, QuestionGroup, Question, StudentSession, Answer, SuspiciousEvent


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['quiz_code', 'title', 'timer_mode', 'quiz_duration', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'timer_mode', 'created_at']
    search_fields = ['quiz_code', 'title', 'created_by__username']
    readonly_fields = ['quiz_code', 'created_at', 'updated_at']


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'name', 'marks_per_question', 'pick_count', 'order']
    list_filter = ['quiz']
    search_fields = ['name', 'quiz__title']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'question_text_short', 'group', 'duration_seconds', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(StudentSession)
class StudentSessionAdmin(admin.ModelAdmin):
    list_display = ['reg_number', 'full_name', 'quiz', 'total_score', 'max_possible_score', 'is_submitted', 'submitted_via', 'start_time']
    list_filter = ['is_submitted', 'submitted_via', 'quiz']
    search_fields = ['reg_number', 'full_name', 'email']
    readonly_fields = ['start_time', 'submitted_at']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'marks_awarded', 'attempts_used', 'time_taken_seconds']
    list_filter = ['is_correct', 'session__quiz']
    search_fields = ['session__reg_number', 'session__full_name']


@admin.register(SuspiciousEvent)
class SuspiciousEventAdmin(admin.ModelAdmin):
    list_display = ['session', 'event_type', 'question_index', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['session__reg_number', 'session__full_name']
    readonly_fields = ['timestamp']

