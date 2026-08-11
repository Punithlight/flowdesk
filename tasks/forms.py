from django import forms
from .models import Task


class TaskUpdateForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            "status",
            "progress",
            "employee_comment",
            "attachment",
        ]

        widgets = {

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "progress": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                    "placeholder": "Enter progress %",
                }
            ),

            "employee_comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add a comment...",
                }
            ),

            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }