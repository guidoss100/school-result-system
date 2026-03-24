from django import forms
from django.contrib.auth.models import User
from .models import Teacher, Subject

LEVEL_CHOICES = (
    ('Primary', 'Primary'),
    ('JHS', 'JHS'),
)

class TeacherSignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Teacher
        fields = ['full_name', 'level', 'subjects']  # Subjects can be multiple

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data