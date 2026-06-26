from django import forms
from .models import Quiz, Question, QuestionGroup, StudentSession


class QuizForm(forms.ModelForm):
    # Pro users get access to more advanced form options (time per group etc)
    quiz_duration = forms.IntegerField(
        min_value=1,
        max_value=300,
        label="Duration (minutes)",
        help_text="Quiz duration in minutes"
    )
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'timer_mode', 'quiz_duration', 'pass_mark', 
                  'randomize_questions', 'randomize_choices']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_quiz_duration(self):
        """Convert minutes to seconds for storage"""
        minutes = self.cleaned_data.get('quiz_duration')
        if minutes:
            return minutes * 60  # Convert to seconds
        return minutes


class QuestionGroupForm(forms.ModelForm):
    class Meta:
        model = QuestionGroup
        fields = ['name', 'marks_per_question', 'pick_count', 'order']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'group', 'option_a', 'option_b', 
                  'option_c', 'option_d', 'correct_answer', 'duration_seconds', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz', None)
        super().__init__(*args, **kwargs)
        if quiz:
            self.fields['group'].queryset = QuestionGroup.objects.filter(quiz=quiz)
        
        # Add help text for True/False questions
        self.fields['question_type'].help_text = 'Select MCQ or True/False'
        self.fields['option_a'].help_text = 'For True/False: Enter "True"'
        self.fields['option_b'].help_text = 'For True/False: Enter "False"'
        self.fields['option_c'].help_text = 'For True/False: Leave blank'
        self.fields['option_d'].help_text = 'For True/False: Leave blank'
        self.fields['correct_answer'].help_text = 'Enter: option_a, option_b, option_c, or option_d'

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
            if option_c or option_d:
                raise forms.ValidationError('True/False questions should only use options A and B')

        # Validate correct answer
        if correct_answer not in ['option_a', 'option_b', 'option_c', 'option_d']:
            raise forms.ValidationError('Correct answer must be one of: option_a, option_b, option_c, option_d')

        return cleaned_data


class StudentEntryForm(forms.Form):
    full_name = forms.CharField(max_length=200, required=True)
    reg_number = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)



