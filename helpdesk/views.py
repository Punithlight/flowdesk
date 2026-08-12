from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from employees.models import Employee
from .models import SupportTicket


# ============================================================
# EMPLOYEE / MANAGER HELP DESK
# ============================================================

@login_required(login_url="login")
def helpdesk(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    tickets = SupportTicket.objects.filter(
        employee=employee
    ).order_by("-created_at")

    context = {
        "tickets": tickets,
    }

    return render(
        request,
        "helpdesk/HelpDesk.html",
        context
    )


# ============================================================
# TEAM LEAD - TECHNICAL SUPPORT
# ============================================================

@login_required(login_url="login")
def TechnicalSupport(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )


    # ========================================================
    # CREATE NEW SUPPORT TICKET
    # ========================================================

    if request.method == "POST":

        subject = request.POST.get(
            "subject",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        ticket_type = request.POST.get(
            "ticket_type",
            "Issue"
        )


        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not subject or not description:

            tickets = SupportTicket.objects.filter(
                employee=employee
            ).order_by("-created_at")

            return render(
                request,
                "helpdesk/TechnicalSupport.html",
                {
                    "tickets": tickets,
                    "error": "Subject and details are required."
                }
            )


        # ----------------------------------------------------
        # Create REAL ticket in database
        # ----------------------------------------------------

        SupportTicket.objects.create(

            employee=employee,

            subject=subject,

            description=description,

            ticket_type=ticket_type

        )


        messages.success(
            request,
            "Support ticket created successfully."
        )


        # ----------------------------------------------------
        # Reload Technical Support page
        # ----------------------------------------------------

        return redirect(
            "helpdesk:technical_support"
        )


    # ========================================================
    # DISPLAY REAL DATABASE TICKETS
    # ========================================================

    tickets = SupportTicket.objects.filter(
        employee=employee
    ).order_by("-created_at")


    context = {
        "tickets": tickets,
    }


    return render(
        request,
        "helpdesk/TechnicalSupport.html",
        context
    )