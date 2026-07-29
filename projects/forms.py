from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project

        fields = [
            'project_name',
            'description',
            'employee',
            'role',
            'progress',
            'status',
            'start_date',
            'end_date',
        ]

        widgets = {

            'project_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter project name'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter project description',
                    'rows': 4
                }
            ),

            'employee': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'role': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter role'
                }
            ),

            'progress': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                    'max': 100
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
        }