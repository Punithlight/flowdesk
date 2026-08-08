from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone


from .models import Schedule
from notifications.models import Notification
from employees.models import Employee

User = get_user_model()



# ======================================================
# MANAGER SCHEDULES
# ======================================================

@login_required(login_url="login")
def manager_schedules(request):

    schedules = Schedule.objects.filter(
        manager=request.user
    ).order_by("-created_at")

    employees = Employee.objects.select_related      ("user").exclude(
                user=request.user
            ).filter(
                role__in=["Employee", "Team Lead"]
            )
    

    # Get local date and time
    now = timezone.localtime()

    return render(
        request,
        "schedules/manager_schedules.html",
        {
            "schedules": schedules,
            "employees": employees,
            "today": now.date(),
            "current_time": now.strftime("%I:%M %p"),
        }
    )





# ======================================================
# EMPLOYEE SCHEDULES
# ======================================================

@login_required(login_url="login")
def employee_schedules(request):

    schedules = Schedule.objects.filter(
        participants=request.user
    ).order_by(
        "meeting_date",
        "start_time"
    )


    return render(
        request,
        "schedules/employee_schedules.html",
        {
            "schedules": schedules
        }
    )





# ======================================================
# CREATE SCHEDULE
# ======================================================

@login_required(login_url="login")
def create_schedule(request):

    if request.method == "POST":


        title = request.POST.get("title")

        description = request.POST.get("description")

        venue = request.POST.get("venue")

        meeting_date = request.POST.get("meeting_date")

        start_time = request.POST.get("start_time")

        end_time = request.POST.get("end_time")



        schedule = Schedule.objects.create(

            title=title,

            description=description,

            manager=request.user,

            venue=venue,

            meeting_date=meeting_date,

            start_time=start_time,

            end_time=end_time,

            status="Upcoming"

        )



        participants = request.POST.getlist(
            "participants"
        )



        if participants:


            users = User.objects.filter(
                id__in=participants
            )


            schedule.participants.set(
                users
            )



        messages.success(
            request,
            "Meeting created successfully"
        )



        return redirect(
            "schedules:manager_schedules"
        )




    employees = User.objects.exclude(
        id=request.user.id
    )



    return render(
        request,
        "schedules/manager_schedules.html",
        {
            "employees": employees
        }
    )






# ======================================================
# SCHEDULE DETAIL
# ======================================================

@login_required(login_url="login")
def schedule_detail(request, id):

    schedule = get_object_or_404(
        Schedule,
        id=id
    )


    return render(
        request,
        "schedules/schedule_detail.html",
        {
            "schedule": schedule
        }
    )







# ======================================================
# DELETE SCHEDULE
# ======================================================

@login_required(login_url="login")
def delete_schedule(request, id):


    schedule = get_object_or_404(
        Schedule,
        id=id
    )



    if request.method == "POST":


        schedule.delete()



        messages.success(
            request,
            "Meeting deleted successfully"
        )



    return redirect(
        "schedules:manager_schedules"
    )







# ======================================================
# NOTIFY ATTENDEES
# ======================================================

@login_required(login_url="login")
def notify_attendees(request, pk):

    meeting = get_object_or_404(
        Schedule,
        id=pk
    )


    participants = meeting.participants.all()


    for user in participants:


        employee = Employee.objects.filter(
            user=user
        ).first()


        if employee:

           Notification.objects.create(
            employee=employee,
            title="Meeting Invitation",
            message=f"""
        You have been invited to a meeting.

        Meeting : {meeting.title}
        Date : {meeting.meeting_date}
        Time : {meeting.start_time} - {meeting.end_time}
        Venue : {meeting.venue}

        Manager : {meeting.manager.get_full_name()}
        """,
            notification_type="Meeting"
        )
   

    meeting=meeting


    messages.success(
        request,
        "Meeting notification sent successfully"
    )


    return redirect(
        "schedules:manager_schedules"
    )