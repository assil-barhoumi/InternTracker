from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Intern

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'First Name',
            'required': True
        })
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Last Name',
            'required': True
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'required': True
        })

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = ['cv']
