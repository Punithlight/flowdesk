from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from employees.models import Employee
from settings.models import ActiveSession
from settings.models import LoginHistory as SettingsLoginHistory

from .models import LoginHistory as AccountLoginHistory
from .models import UserProfile


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR", "127.0.0.1")


def get_device(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    if "Mobile" in user_agent:
        return "Mobile Device"

    if "Windows" in user_agent:
        return "Windows Computer"

    if "Macintosh" in user_agent:
        return "Mac Computer"

    if "Linux" in user_agent:
        return "Linux Computer"

    return "Unknown Device"


def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password,
            )

            if user is None:
                messages.error(request, "Invalid password.")
                return redirect("login")

            profile = UserProfile.objects.get(user=user)

            if profile.role != role:
                messages.error(
                    request,
                    "Selected role does not match your account."
                )
                return redirect("login")

            login(request, user)
            print("========== LOGIN ==========")
            print("Logged in User ID:", user.id)
            print("Logged in Email:", user.email)
            print("request.user:", request.user.id, request.user.email)
            

            ip_address = get_client_ip(request)
            device = get_device(request)

            location = (
                "Local Network"
                if ip_address in ("127.0.0.1", "::1")
                else "Unknown"
            )

            # Existing accounts-app login history
            AccountLoginHistory.objects.create(
                user=user,
                role=profile.role,
            )

            # Settings-page login history
            SettingsLoginHistory.objects.create(
                user=user,
                device=device,
                location=location,
                ip_address=ip_address,
            )

            if not request.session.session_key:
                request.session.save()

            ActiveSession.objects.filter(user=user).update(
                is_current=False
            )

            ActiveSession.objects.update_or_create(
                user=user,
                session_key=request.session.session_key,
                defaults={
                    "device": device,
                    "location": location,
                    "ip_address": ip_address,
                    "is_current": True,
                },
            )

            if profile.role == "employee":
                return redirect("employee_dashboard")

            if profile.role == "manager":
                return redirect("manager_dashboard")

            if profile.role == "admin":
                return redirect("admin_dashboard")

            if profile.role == "team lead":
                return redirect("teamlead_dashboard")

            if profile.role == "hr":
                return redirect("hr_dashboard")

            messages.error(request, "Invalid user role.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("login")

        except UserProfile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect("login")

    return render(request, "accounts/login.html")


def signup(request):

    if request.method == "POST":

        full_name = request.POST["full_name"]
        email = request.POST["email"]
        role = request.POST["role"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("signup")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )

        user.first_name = full_name
        user.save()

        UserProfile.objects.create(
            user=user,
            role=role,
        )

        employee_count = Employee.objects.count() + 1

        Employee.objects.create(
            user=user,
            employee_id=f"EMP{employee_count:03d}",
            department="General",
            designation=role,
            role=role.title(),
            phone="0000000000",
            joining_date=date.today(),
        )

        messages.success(request, "Account Created Successfully.")
        return redirect("login")

    return render(request, "accounts/signup.html")


def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("forgot_password")

        try:
            user = User.objects.get(email=email)

            user.set_password(new_password)
            user.save()

            messages.success(request, "Password updated successfully.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "Email does not exist.")

    return render(request, "accounts/forgot_password.html")


def logout_view(request):
    logout(request)
    return redirect("login")