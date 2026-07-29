from django import forms
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):

    class Meta:

        model = LeaveRequest


        fields = [
            "leave_type",
            "from_date",
            "to_date",
            "description",
            "attachment"
        ]


        widgets = {

            "from_date": forms.DateInput(
                attrs={
                    "type":"date",
                    "class":"form-control"
                }
            ),


            "to_date": forms.DateInput(
                attrs={
                    "type":"date",
                    "class":"form-control"
                }
            ),


            "description": forms.TextInput(
                attrs={
                    "placeholder":"Brief reason for leave"
                }
            )

        }