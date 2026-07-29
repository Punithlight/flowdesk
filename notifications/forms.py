from django import forms
from django.contrib.auth.models import User

class NotificationForm(forms.Form):

    employee = forms.ModelChoiceField(
        queryset=User.objects.all()
    )

    title = forms.CharField(max_length=200)

    message = forms.CharField(
        widget=forms.Textarea
    )

    priority = forms.ChoiceField(
        choices=[
            ('Low','Low'),
            ('Medium','Medium'),
            ('High','High')
        ]
    )