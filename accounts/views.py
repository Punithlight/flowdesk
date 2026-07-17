from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages

from .models import UserProfile
from .models import LoginHistory


def login_view(request):

    if request.method == "POST":

        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                username=user_obj.username,
                password=password
            )

            if user is not None:

                profile = UserProfile.objects.get(user=user)
                LoginHistory.objects.create(
                     user=user,
                     role=profile.role
                )
                if profile.role == role:

                    login(request, user)

                    return redirect("dashboard")

                else:
                    messages.error(request, "Role does not match.")

            else:

                messages.error(request, "Invalid Password.")

        except User.DoesNotExist:

            messages.error(request, "User not found.")

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

        username = email

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = full_name

        user.save()

        UserProfile.objects.create(
            user=user,
            role=role
        )

        messages.success(request, "Account Created Successfully.")

        return redirect("login")

    return render(request, "accounts/signup.html")


def forgot_password(request):

    if request.method == "POST":

        email = request.POST["email"]
        new_password = request.POST["new_password"]
        confirm = request.POST["confirm_password"]

        if new_password != confirm:

            messages.error(request, "Passwords do not match.")

            return redirect("forgot_password")

        try:

            user = User.objects.get(email=email)

            user.set_password(new_password)

            user.save()

            messages.success(request, "Password Updated Successfully.")

            return redirect("login")

        except User.DoesNotExist:

            messages.error(request, "Email does not exist.")

    return render(request, "accounts/forgot_password.html")