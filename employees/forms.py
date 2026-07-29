from django import forms
from .models import Employee


# ==========================
# Employee Profile Form
# ==========================

class EmployeeProfileForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "department",
            "designation",
            "phone",
            "profile_image",
        ]

        widgets = {

            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Department",
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Designation",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                }
            ),

            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# ==========================
# Personal Information Form
# ==========================

class PersonalInfoForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "dob",
            "gender",
            "blood_group",
            "present_address",
            "permanent_address",
            "city",
            "state",
            "country",
            "emergency_contact_name",
            "emergency_contact",
        ]

        widgets = {

            "dob": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "blood_group": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "present_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                }
            ),

            "permanent_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "emergency_contact": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# ==========================
# Professional Details Form
# ==========================

class ProfessionalDetailsForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "reporting_manager",
            "team_name",
            "work_location",
            "employment_type",
        ]

        widgets = {

            "reporting_manager": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "team_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "work_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "employment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }