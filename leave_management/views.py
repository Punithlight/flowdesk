from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import LeaveRequest
from .forms import LeaveRequestForm


# =====================================
# EMPLOYEE LEAVE DASHBOARD
# =====================================

@login_required(login_url="login")
def leave_dashboard(request):

    leaves = LeaveRequest.objects.filter(
        employee=request.user
    ).order_by("-applied_on")

    pending_count = leaves.filter(
        status="Pending"
    ).count()

    approved_count = leaves.filter(
        status="Approved"
    ).count()

    rejected_count = leaves.filter(
        status="Rejected"
    ).count()

    total_leave = 20
    used_leave = approved_count
    available_leave = total_leave - used_leave

    if request.method == "POST":

        form = LeaveRequestForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            leave = form.save(commit=False)

            leave.employee = request.user
            leave.status = "Pending"

            leave.save()

            messages.success(
                request,
                "Leave request submitted successfully."
            )

            return redirect("leave_dashboard")

    else:

        form = LeaveRequestForm()

    context = {

        "leaves": leaves,

        "form": form,

        "pending_count": pending_count,

        "approved_count": approved_count,

        "rejected_count": rejected_count,

        "available_leave": available_leave,

        "used_leave": used_leave,

        "total_leave": total_leave,

    }

    return render(
        request,
        "leave_management/leave_dashboard.html",
        context
    )


# =====================================
# MANAGER LEAVE APPROVAL
# =====================================

@login_required(login_url="login")
def manager_leave_requests(request):

    pending_requests = LeaveRequest.objects.filter(
        status="Pending"
    ).order_by("-applied_on")

    context = {

        "pending_requests": pending_requests

    }

    return render(
        request,
        "leave_management/manager_leave_requests.html",
        context
    )


# =====================================
# APPROVE LEAVE
# =====================================

@login_required(login_url="login")
def approve_leave(request, pk):

    leave = get_object_or_404(
        LeaveRequest,
        pk=pk
    )

    leave.status = "Approved"

    leave.save()

    messages.success(
        request,
        "Leave request approved successfully."
    )

    return redirect("manager_leave_requests")


# =====================================
# REJECT LEAVE
# =====================================

@login_required(login_url="login")
def reject_leave(request, pk):

    leave = get_object_or_404(
        LeaveRequest,
        pk=pk
    )

    leave.status = "Rejected"

    leave.save()

    messages.warning(
        request,
        "Leave request rejected."
    )

    return redirect("manager_leave_requests")