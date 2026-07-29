from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.attendance_dashboard,
        name="attendance_dashboard"
    ),

    path(
        "check-in/",
        views.check_in,
        name="check_in"
    ),

    path(
        "start-break/",
        views.start_break,
        name="start_break"
    ),

    path(
        "end-break/",
        views.end_break,
        name="end_break"
    ),

    path(
        "check-out/",
        views.check_out,
        name="check_out"
    ),

]