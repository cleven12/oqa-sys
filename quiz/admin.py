from django.contrib import admin
from .models import Quiz, QuestionGroup, Question, StudentSession, Answer, SuspiciousEvent


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['quiz_code', 'title', 'timer_mode', 'quiz_duration', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'timer_mode', 'created_at']
    search_fields = ['quiz_code', 'title', 'created_by__username']
    readonly_fields = ['quiz_code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'quiz_code', 'created_by')
        }),
        ('Timer Settings', {
            'fields': ('timer_mode', 'quiz_duration', 'pass_mark')
        }),
        ('Randomization', {
            'fields': ('randomize_questions', 'randomize_choices')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'name', 'marks_per_question', 'pick_count', 'order']
    list_filter = ['quiz']
    search_fields = ['name', 'quiz__title']
    
    fieldsets = (
        (None, {
            'fields': ('quiz', 'name', 'order')
        }),
        ('Question Selection', {
            'fields': ('pick_count', 'marks_per_question'),
            'description': 'Define how many questions to randomly pick from this group and their marks'
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'question_text_short', 'group', 'correct_answer', 'order']
    list_filter = ['question_type', 'quiz', 'group']
    search_fields = ['question_text', 'quiz__title']
    list_editable = ['order']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('quiz', 'group', 'question_type', 'question_text', 'order')
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'description': 'For MCQ: Fill all 4 options. For True/False: Use only option_a (True) and option_b (False)'
        }),
        ('Correct Answer', {
            'fields': ('correct_answer',),
            'description': 'Enter: option_a, option_b, option_c, or option_d'
        }),
        ('Timer (Optional)', {
            'fields': ('duration_seconds',),
            'classes': ('collapse',),
            'description': 'Set per-question timer in seconds (leave blank for no timer)'
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add helpful text for true/false questions
        if obj and obj.question_type == 'true_false':
            form.base_fields['option_a'].help_text = 'Enter: True'
            form.base_fields['option_b'].help_text = 'Enter: False'
            form.base_fields['option_c'].help_text = 'Leave blank for True/False questions'
            form.base_fields['option_d'].help_text = 'Leave blank for True/False questions'
        
        return form


@admin.register(StudentSession)
class StudentSessionAdmin(admin.ModelAdmin):
    list_display = ['reg_number', 'full_name', 'quiz', 'total_score', 'max_possible_score', 'percentage', 'is_submitted', 'submitted_via', 'start_time']
    list_filter = ['is_submitted', 'submitted_via', 'quiz', 'quiz__created_by']
    search_fields = ['reg_number', 'full_name', 'email']
    readonly_fields = ['start_time', 'submitted_at', 'total_score', 'max_possible_score', 'percentage']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Student Information', {
            'fields': ('full_name', 'reg_number', 'email')
        }),
        ('Quiz Information', {
            'fields': ('quiz', 'start_time', 'submitted_at')
        }),
        ('Score Information', {
            'fields': ('total_score', 'max_possible_score', 'percentage')
        }),
        ('Status', {
            'fields': ('is_submitted', 'submitted_via', 'current_question_index')
        }),
    )
    
    def percentage(self, obj):
        return f"{obj.percentage_score}%"
    percentage.short_description = 'Score %'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['session_info', 'question_short', 'chosen_answer', 'is_correct', 'marks_awarded', 'time_taken_seconds']
    list_filter = ['is_correct', 'session__quiz']
    search_fields = ['session__reg_number', 'session__full_name', 'question__question_text']
    readonly_fields = ['created_at', 'updated_at']
    
    def session_info(self, obj):
        return f"{obj.session.reg_number} - {obj.session.full_name}"
    session_info.short_description = 'Student'
    
    def question_short(self, obj):
        return obj.question.question_text[:40] + '...' if len(obj.question.question_text) > 40 else obj.question.question_text
    question_short.short_description = 'Question'


@admin.register(SuspiciousEvent)
class SuspiciousEventAdmin(admin.ModelAdmin):
    list_display = ['session_info', 'event_type', 'question_index', 'timestamp']
    list_filter = ['event_type', 'timestamp', 'session__quiz']
    search_fields = ['session__reg_number', 'session__full_name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def session_info(self, obj):
        return f"{obj.session.reg_number} - {obj.session.full_name}"
    session_info.short_description = 'Student'

