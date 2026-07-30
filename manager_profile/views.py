from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employee


@login_required(login_url="login")
def manager_profile(request):
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, "manager_profile/profile.html", {"employee": employee})


@login_required(login_url="login")
def edit_profile(request):
    employee = get_object_or_404(Employee, user=request.user)

    if request.method == "POST":
        employee.designation = request.POST.get("designation", employee.designation)
        employee.department = request.POST.get("department", employee.department)
        employee.phone = request.POST.get("mobile", employee.phone)
        employee.joining_date = request.POST.get("doj", employee.joining_date)

        # Update name on the User object
        full_name = request.POST.get("name", "").strip()
        if full_name:
            parts = full_name.split(" ", 1)
            employee.user.first_name = parts[0]
            employee.user.last_name = parts[1] if len(parts) > 1 else ""
            employee.user.save()

        employee.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("manager_profile")

    return render(request, "manager_profile/editprofile.html", {"employee": employee})


@login_required(login_url="login")
def personal_info(request):
    employee = get_object_or_404(Employee, user=request.user)

    if request.method == "POST":
        employee.dob = request.POST.get("dob") or None
        employee.gender = request.POST.get("gender", employee.gender)
        employee.blood_group = request.POST.get("bloodGroup", employee.blood_group)
        employee.present_address = request.POST.get("presentAddress", employee.present_address)
        employee.permanent_address = request.POST.get("permanentAddress", employee.permanent_address)
        employee.city = request.POST.get("city", employee.city)
        employee.state = request.POST.get("state", employee.state)
        employee.country = request.POST.get("country", employee.country)
        employee.emergency_contact_name = request.POST.get("emergencyContactName", employee.emergency_contact_name)
        employee.emergency_contact = request.POST.get("emergencyContactNumber", employee.emergency_contact)
        employee.save()
        messages.success(request, "Personal information saved.")
        return redirect("manager_profile")

    return render(request, "manager_profile/personal-info.html", {"employee": employee})


@login_required(login_url="login")
def update_details(request):
    employee = get_object_or_404(Employee, user=request.user)

    if request.method == "POST":
        employee.reporting_manager = request.POST.get("manager", employee.reporting_manager)
        employee.team_name = request.POST.get("team", employee.team_name)
        employee.work_location = request.POST.get("location", employee.work_location)
        employee.employment_type = request.POST.get("employmentType", employee.employment_type)
        employee.save()
        messages.success(request, "Details updated successfully.")
        return redirect("manager_profile")

    return render(request, "manager_profile/updatedetails.html", {"employee": employee})


@login_required(login_url="login")
def change_password(request):

    if request.method == "POST":
        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("manager_change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("manager_change_password")

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect("manager_change_password")

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully.")
        return redirect("manager_profile")

    return render(request, "manager_profile/changepassword.html")
