from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import CalendarEvent
from leave_management.models import LeaveRequest


@login_required
def calendar_dashboard(request):

    today = timezone.localdate()

    # # Today's Events
    # today_events = CalendarEvent.objects.filter(
    #     employee=request.user,
    #     start_date=today
    # )

    # # Upcoming Meetings
    # upcoming_meetings = CalendarEvent.objects.filter(
    #     employee=request.user,
    #     event_type="Meeting",
    #     start_date__gte=today
    # ).order_by("start_date")[:5]

    # # Holidays
    # holidays = CalendarEvent.objects.filter(
    #     event_type="Holiday",
    #     start_date__gte=today
    # ).order_by("start_date")

    # # Leave Information (from Leave Management app)
    # leave_info = LeaveRequest.objects.filter(
    #     employee=request.user,
    #     status="Approved"
    # ).order_by("from_date")

    # # Reminders
    # reminders = CalendarEvent.objects.filter(
    #     employee=request.user,
    #     event_type="Reminder",
    #     start_date__gte=today
    # ).order_by("start_date")

    # All calendar events
    events = CalendarEvent.objects.filter(
        employee=request.user
    )

    context = {
        "today": today,
        # "today_events": today_events,
        # "upcoming_meetings": upcoming_meetings,
        # "holidays": holidays,
        # "leave_info": leave_info,
        # "reminders": reminders,
        "events": events,
    }

    return render(request, "Calendar_app/Calendar.html", context)