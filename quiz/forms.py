from django import forms
from .models import Quiz, Question, QuestionGroup, StudentSession


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'timer_mode', 'quiz_duration', 'pass_mark', 
                  'randomize_questions', 'randomize_choices']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'quiz_duration': forms.NumberInput(attrs={'help_text': 'Duration in seconds'}),
        }


class QuestionGroupForm(forms.ModelForm):
    class Meta:
        model = QuestionGroup
        fields = ['name', 'marks_per_question', 'pick_count', 'order']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'group', 'option_a', 'option_b', 
                  'option_c', 'option_d', 'correct_answer', 'duration_seconds', 
                  'max_attempts', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz', None)
        super().__init__(*args, **kwargs)
        if quiz:
            self.fields['group'].queryset = QuestionGroup.objects.filter(quiz=quiz)


class StudentEntryForm(forms.Form):
    full_name = forms.CharField(max_length=200, required=True)
    reg_number = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        required=True,
        help_text='Upload Excel file with questions'
    )
