from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # MY TASK
    # ======================================================

    path(
        "my-task/",
        views.my_task,
        name="my_task"
    ),

    # ======================================================
    # UPDATE
    # ======================================================

    path(
        "update/<int:pk>/",
        views.update_task,
        name="update_task"
    ),

    # ======================================================
    # TASK DETAIL
    # ======================================================

    path(
        "detail/<int:pk>/",
        views.task_detail,
        name="task_detail"
    ),

    # ======================================================
    # EXPORT
    # ======================================================

    path(
        "export/",
        views.export,
        name="export"
    ),

    # ======================================================
    # APPROVAL DASHBOARD
    # ======================================================

    path(
        "approval/",
        views.approval_dashboard,
        name="approval_dashboard"
    ),

    # ======================================================
    # TASK APPROVAL
    # ======================================================

    path(
        "task-approval/",
        views.task_approval,
        name="task_approval"
    ),

    # ======================================================
    # TASK COMPLETION APPROVAL
    # ======================================================

    path(
        "task-completion-approval/",
        views.task_completion_approval,
        name="task_completion_approval"
    ),

    # ======================================================
    # APPROVE
    # ======================================================

    path(
        "task/<int:pk>/approve/",
        views.approve_completed_task,
        name="approve_completed_task"
    ),

    # ======================================================
    # REJECT
    # ======================================================

    path(
        "task/<int:pk>/reject/",
        views.reject_completed_task,
        name="reject_completed_task"
    ),

    # ======================================================
    # TIMESHEET
    # ======================================================

    path(
        "timesheet-approval/",
        views.timesheet_approval,
        name="timesheet_approval"
    ),

    path(
        "timesheet/<int:pk>/approve/",
        views.approve_timesheet,
        name="approve_timesheet"
    ),

    path(
        "timesheet/<int:pk>/reject/",
        views.reject_timesheet,
        name="reject_timesheet"
    ),

    # ======================================================
    # TEAM LEAD MY TASK
    # ======================================================

    path(
        "team-my-task/",
        views.team_mytaskpage,
        name="team_mytaskpage"
    ),
]