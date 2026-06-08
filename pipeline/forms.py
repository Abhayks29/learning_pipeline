from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Episode, StageSubmission, UserProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}))


class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ['title', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Episode title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Brief description'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'python, beginner, oop'}),
        }


class StageSubmissionForm(forms.ModelForm):
    class Meta:
        model = StageSubmission
        fields = ['file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Any notes for the next team...'}),
            'file': forms.FileInput(attrs={'class': 'form-file'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['team']
        widgets = {
            'team': forms.Select(attrs={'class': 'form-input'}),
        }
