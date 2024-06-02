from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import Customer, user_info

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




class UserRegistrationForm(forms.ModelForm):
    COURSE_CHOICES = [
        ('BS Digital Illustration and Animation', 'BS Digital Illustration and Animation'),
        ('BS Computer Science', 'BS Computer Science'),
        ('BS Information Technology', 'BS Information Technology'),
        ('BS Information Systems', 'BS Information Systems'),
        ('Others', 'Others'),
    ]

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True, help_text='Use GBOX whenever possible.')
    username = forms.CharField(max_length=30, required=True, help_text='Use GBOX Username whenever possible.')
    phone = forms.CharField(max_length=15, required=True)
    course = forms.ChoiceField(choices=COURSE_CHOICES, required=True,  help_text='Select "Others" if not applicable.')
    password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text='Assign a password if the user will be staff. If not a random password will be generated.')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text='Re-enter your password for confirmation.')
    is_staff = forms.BooleanField(required=False, label='Is Staff:', help_text='Check if the user will have staff privileges.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'phone', 'course', 'password', 'confirm_password', 'is_staff')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password do not match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'is_active']

class CustomerForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'readonly': 'readonly'}))

    class Meta:
        model = Customer
        fields = ['user', 'phone', 'course']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'course': forms.TextInput(attrs={'class': 'block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['user'].disabled = True