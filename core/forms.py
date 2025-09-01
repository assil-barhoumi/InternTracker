from django import forms
from .models import Intern, InternshipApplication

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = ['cv']  
