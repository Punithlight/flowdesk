from django import forms
from .models import TimesheetEntry


class TimesheetEntryForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = [
            "task",
            "clock_in",
            "clock_out",
            "break_minutes",
            "notes",
        ]

        widgets = {
            "task": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task name"
                }
            ),

            "clock_in": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                },
                format="%H:%M"
            ),

            "clock_out": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                },
                format="%H:%M"
            ),

            "break_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Break (minutes)"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter work notes"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        clock_in = cleaned_data.get("clock_in")
        clock_out = cleaned_data.get("clock_out")

        if clock_in and clock_out:
            if clock_out <= clock_in:
                raise forms.ValidationError(
                    "Clock Out time must be later than Clock In time."
                )

        return cleaned_data