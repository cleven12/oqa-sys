from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string


class Quiz(models.Model):
    TIMER_MODE_CHOICES = [
        ('quiz', 'Quiz Timer Only'),
        ('question', 'Per-Question Timer Only'),
        ('both', 'Both Quiz and Question Timers'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    quiz_code = models.CharField(max_length=10, unique=True, editable=False)
    timer_mode = models.CharField(max_length=10, choices=TIMER_MODE_CHOICES, default='quiz')
    quiz_duration = models.IntegerField(
        help_text="Total quiz duration in seconds",
        validators=[MinValueValidator(60)]
    )
    pass_mark = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pass percentage (0-100)"
    )
    randomize_questions = models.BooleanField(default=True)
    randomize_choices = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.quiz_code:
            self.quiz_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        while True:
            code = 'QZ-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Quiz.objects.filter(quiz_code=code).exists():
                return code

    def __str__(self):
        return f"{self.quiz_code} - {self.title}"

    class Meta:
        db_table = 'quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']


class QuestionGroup(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100, help_text="e.g., 'Easy', 'Section A', 'Hard'")
    marks_per_question = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="All questions in this group share the same marks"
    )
    pick_count = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="How many questions to randomly pick from this group per student"
    )
    order = models.IntegerField(default=0, help_text="Display order")

    def __str__(self):
        return f"{self.quiz.quiz_code} - {self.name} ({self.pick_count} questions)"

    class Meta:
        db_table = 'question_group'
        verbose_name = 'Question Group'
        verbose_name_plural = 'Question Groups'
        ordering = ['quiz', 'order']
        unique_together = ['quiz', 'name']


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    group = models.ForeignKey(
        QuestionGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    
    # MCQ options
    option_a = models.CharField(max_length=500, blank=True, null=True)
    option_b = models.CharField(max_length=500, blank=True, null=True)
    option_c = models.CharField(max_length=500, blank=True, null=True)
    option_d = models.CharField(max_length=500, blank=True, null=True)
    
    correct_answer = models.CharField(max_length=500)
    duration_seconds = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(5)],
        help_text="Per-question timer (optional)"
    )
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quiz.quiz_code} - Q{self.order}: {self.question_text[:50]}"

    class Meta:
        db_table = 'question'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['quiz', 'order']


class StudentSession(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('manual', 'Manual Submission'),
        ('auto_quiz', 'Auto - Quiz Timer Expired'),
        ('auto_question', 'Auto - Question Timer Expired'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    full_name = models.CharField(max_length=200)
    reg_number = models.CharField(max_length=50)
    email = models.EmailField()
    start_time = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_via = models.CharField(
        max_length=20, 
        choices=SUBMISSION_TYPE_CHOICES, 
        null=True, 
        blank=True
    )
    total_score = models.IntegerField(default=0)
    max_possible_score = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    current_question_index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.reg_number} - {self.full_name} ({self.quiz.quiz_code})"

    @property
    def percentage_score(self):
        if self.max_possible_score > 0:
            return round((self.total_score / self.max_possible_score) * 100, 2)
        return 0

    @property
    def is_passed(self):
        return self.percentage_score >= self.quiz.pass_mark

    @property
    def time_remaining(self):
        if self.is_submitted:
            return 0
        elapsed = (timezone.now() - self.start_time).total_seconds()
        remaining = self.quiz.quiz_duration - elapsed
        return max(0, int(remaining))

    class Meta:
        db_table = 'student_session'
        verbose_name = 'Student Session'
        verbose_name_plural = 'Student Sessions'
        unique_together = ['quiz', 'reg_number']
        ordering = ['-start_time']


class Answer(models.Model):
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    chosen_answer = models.CharField(max_length=500, blank=True, null=True)
    time_taken_seconds = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.session.reg_number} - Q{self.question.order} - {'✓' if self.is_correct else '✗'}"

    class Meta:
        db_table = 'answer'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        unique_together = ['session', 'question']


class SuspiciousEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('tab_switch', 'Tab Switch'),
        ('window_blur', 'Window Blur'),
        ('shortcut_blocked', 'Keyboard Shortcut Blocked'),
        ('copy_attempt', 'Copy Attempt'),
        ('paste_attempt', 'Paste Attempt'),
    ]

    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='suspicious_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    question_index = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.session.reg_number} - {self.event_type} at Q{self.question_index}"

    class Meta:
        db_table = 'suspicious_event'
        verbose_name = 'Suspicious Event'
        verbose_name_plural = 'Suspicious Events'
        ordering = ['-timestamp']
