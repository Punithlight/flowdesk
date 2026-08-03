from django.urls import path
from . import views

urlpatterns = [

    # Employee Leave Dashboard
    path(
        "",
        views.leave_dashboard,
        name="leave_dashboard"
    ),

    # Manager Leave Approval Dashboard
    path(
        "manager-leave-requests/",
        views.manager_leave_requests,
        name="manager_leave_requests"
    ),

    # Approve Leave
    path(
        "approve/<int:pk>/",
        views.approve_leave,
        name="approve_leave"
    ),

    # Reject Leave
    path(
        "reject/<int:pk>/",
        views.reject_leave,
        name="reject_leave"
    ),

]