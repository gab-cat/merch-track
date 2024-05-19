from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import user_info

class CreateUserForm(UserCreationForm):
    student_id = forms.CharField(
        max_length=9, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'rounded-lg'}),
        validators=[RegexValidator(r'^[0-9]{1,9}$', 'Student ID must be numeric and have at most 9 digits.')]
    )
    student_name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'rounded-lg'}))
    course = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'rounded-lg'}))

    class Meta:
        model = User
        fields = ['student_id', 'student_name', 'email', 'password1', 'password2', 'course']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'rounded-lg mx-3'}),
            'student_name': forms.TextInput(attrs={'class': 'rounded-lg mx-3'}),
            'email': forms.EmailInput(attrs={'class': 'rounded-lg'}),
            'password1': forms.PasswordInput(attrs={'class': 'rounded-lg'}),
            'password2': forms.PasswordInput(attrs={'class': 'rounded-lg'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['student_id']  # Set username to student_id
        if commit:
            user.save()
            user_info.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                student_name=self.cleaned_data['student_name'],
                course=self.cleaned_data['course'],
                email=self.cleaned_data['email']
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'w-full rounded-lg', 'placeholder': 'Student ID'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))