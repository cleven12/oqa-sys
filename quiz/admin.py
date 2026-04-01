from django.contrib import admin
from django.db import models
from django import forms
from .models import Quiz, QuestionGroup, Question, StudentSession, Answer, SuspiciousEvent


class QuestionAdminForm(forms.ModelForm):
    """Custom form for Question admin with dynamic field handling"""
    
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'option_a': forms.TextInput(attrs={'size': 60}),
            'option_b': forms.TextInput(attrs={'size': 60}),
            'option_c': forms.TextInput(attrs={'size': 60}),
            'option_d': forms.TextInput(attrs={'size': 60}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        option_a = cleaned_data.get('option_a')
        option_b = cleaned_data.get('option_b')
        option_c = cleaned_data.get('option_c')
        option_d = cleaned_data.get('option_d')
        correct_answer = cleaned_data.get('correct_answer')

        if question_type == 'mcq':
            # MCQ requires all 4 options
            if not all([option_a, option_b, option_c, option_d]):
                raise forms.ValidationError('Multiple Choice questions require all 4 options (A, B, C, D)')
        
        elif question_type == 'true_false':
            # True/False requires only option_a and option_b
            if not option_a or not option_b:
                raise forms.ValidationError('True/False questions require option A (True) and option B (False)')
            
            # Auto-clear options C and D for true/false
            cleaned_data['option_c'] = None
            cleaned_data['option_d'] = None

        # Validate correct answer
        if correct_answer:
            valid_options = ['option_a', 'option_b']
            if question_type == 'mcq':
                valid_options.extend(['option_c', 'option_d'])
            
            if correct_answer not in valid_options:
                raise forms.ValidationError(f'Correct answer must be one of: {", ".join(valid_options)}')

        return cleaned_data


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
        ('Question Selection & Scoring', {
            'fields': ('pick_count', 'marks_per_question'),
            'description': 'Define how many questions to randomly pick from this group and their marks'
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    change_form_template = 'admin/quiz/question/change_form.html'
    
    list_display = ['question_text_short', 'question_type_display', 'quiz', 'group', 'correct_answer', 'order']
    list_filter = ['question_type', 'quiz', 'group']
    search_fields = ['question_text', 'quiz__title']
    list_editable = ['order']
    ordering = ['quiz', 'order']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('quiz', 'group', 'question_type', 'question_text', 'order'),
            'description': 'Select question type first to see relevant option fields'
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'description': 'MCQ: All 4 options required | True/False: Only A (True) and B (False) required'
        }),
        ('Correct Answer', {
            'fields': ('correct_answer',),
            'description': 'Enter: option_a, option_b, option_c, or option_d'
        }),
        ('Advanced Settings', {
            'fields': ('duration_seconds',),
            'classes': ('collapse',),
            'description': 'Optional: Set per-question timer in seconds'
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:60] + '...' if len(obj.question_text) > 60 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def question_type_display(self, obj):
        type_colors = {
            'mcq': '🔵 MCQ',
            'true_false': '🟢 True/False'
        }
        return type_colors.get(obj.question_type, obj.question_type)
    question_type_display.short_description = 'Type'


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

