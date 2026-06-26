from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import TeacherProfile


class TeacherRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    institution = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                institution=self.cleaned_data.get('institution')
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username or Email",
        help_text="Enter your username or email address"
    )
    password = forms.CharField(widget=forms.PasswordInput)
