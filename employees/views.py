from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .models import Employee
from .forms import (
    EmployeeProfileForm,
    PersonalInfoForm,
    ProfessionalDetailsForm,
)


# ===========================
# Employee Profile
# ===========================

@login_required(login_url="login")
def employees_profile(request):
    employee = Employee.objects.get(user=request.user)

    return render(
        request,
        "employees/profile.html",
        {
            "employee": employee
        }
    )

# ===========================
# Edit Profile
# ===========================

@login_required(login_url="login")
def edit_profile(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    if request.method == "POST":

        form = EmployeeProfileForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("employees_profile")

    else:

        form = EmployeeProfileForm(
            instance=employee
        )

    return render(
        request,
        "employees/edit-profile.html",
        {
            "form": form,
            "employee": employee,
        }
    )


# ===========================
# Personal Information
# ===========================

@login_required(login_url="login")
def personal_info(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    if request.method == "POST":

        form = PersonalInfoForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Personal information updated successfully."
            )

            return redirect("employees_profile")

    else:

        form = PersonalInfoForm(
            instance=employee
        )

    return render(request, "employees/personal-info.html", {
        "form": form,
        "employee": employee,
    })

# ===========================
# Professional Details
# ===========================

@login_required(login_url="login")
def update_details(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    if request.method == "POST":

        form = ProfessionalDetailsForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Professional details updated successfully."
            )

            return redirect("employee_profile")

    else:

        form = ProfessionalDetailsForm(
            instance=employee
        )

    return render(
        request,
        "employees/update-details.html",
        {
            "form": form,
            "employee": employee,
        }
    )


# ===========================
# Change Password
# ===========================

@login_required(login_url="login")
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        # Add CSS classes
        form.fields["old_password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Current Password"
        })

        form.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "New Password"
        })

        form.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm New Password"
        })

        if form.is_valid():

            user = form.save()

            # Keep user logged in
            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("employee_profile")

        else:

            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = PasswordChangeForm(request.user)

        # Add CSS classes
        form.fields["old_password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Current Password"
        })

        form.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "New Password"
        })

        form.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm New Password"
        })

    return render(
        request,
        "employees/change-password.html",
        {
            "form": form,
        }
    )