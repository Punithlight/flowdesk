from django.urls import path
from . import views

urlpatterns = [

    # Employee Tasks
    path(
        "mytask/",
        views.mytask,
        name="mytask"
    ),

    path(
        "update/<int:pk>/",
        views.update_task,
        name="update_task"
    ),

    path(
        "export/",
        views.export,
        name="export"
    ),

    # Approval Dashboard
    path(
        "approval/",
        views.approval_dashboard,
        name="approval_dashboard"
    ),

    # Task Approval Dashboard
    path(
        "task-approval/",
        views.task_approval,
        name="task_approval"
    ),

    # Task Completion Approval
    path(
        "task-completion-approval/",
        views.task_completion_approval,
        name="task_completion_approval"
    ),

    # Approve Task
    path(
        "approve-task/<int:pk>/",
        views.approve_completed_task,
        name="approve_completed_task"
    ),

    # Reject Task
    path(
        "reject-task/<int:pk>/",
        views.reject_completed_task,
        name="reject_completed_task"
    ),

]