from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import LeaveRequest
from .forms import LeaveRequestForm



@login_required
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


            return redirect(
                "leave_dashboard"
            )


    else:

        form = LeaveRequestForm()



    context = {

        "leaves": leaves,

        "form": form,

        "pending_count": pending_count,

        "approved_count": approved_count,

        "available_leave": available_leave,

        "total_leave": total_leave,

        "used_leave": used_leave,

    }



    return render(
        request,
        "leave_management/leave_dashboard.html",
        context
    )