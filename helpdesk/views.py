from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employees.models import Employee
from .models import SupportTicket


@login_required
def helpdesk(request):
    employee = Employee.objects.get(user=request.user)

    tickets = SupportTicket.objects.filter(
        employee=employee
    ).order_by("-created_at")

    context = {
        "tickets": tickets,
    }

    return render(request, "helpdesk/helpdesk.html", context)