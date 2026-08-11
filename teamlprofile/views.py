from django.shortcuts import render

# Create your views here.

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employee


@login_required(login_url="login")
def teamlead_profile(request):
    employee = get_object_or_404(
        Employee,
        user=request.user,
        role="Team Lead"
    )

    return render(
        request,
        "teamlprofile/profile.html",
        {"employee": employee}
    )

