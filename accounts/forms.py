from django import forms

class LoginForm(forms.Form):

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    role = forms.CharField()


class SignupForm(forms.Form):

    full_name = forms.CharField()

    email = forms.EmailField()

    role = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField()

    new_password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )