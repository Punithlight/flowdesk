# from django.urls import path
# from . import views

# urlpatterns = [
#     path("employee/", views.employee_dashboard, name="employee_dashboard"),
#     path("manager/", views.manager_dashboard, name="manager_dashboard"),
#     # path("admin/", views.admin_dashboard, name="admin_dashboard"),
#     # path("teamlead/", views.teamlead_dashboard, name="teamlead_dashboard"),
#     # path("hr/", views.hr_dashboard, name="hr_dashboard"),

#     path("mytask/", views.mytask, name="mytask"),
#     path("helpdesk/", helpdesk_views.helpdesk, name="helpdesk"),

   
# ]

from django.urls import path
from . import views

urlpatterns = [

    path(
        "employee/",
        views.employee_dashboard,
        name="employee_dashboard"
    ),

    path(
        "manager/",
        views.manager_dashboard,
        name="manager_dashboard"
    ),

    path(
        "teamlead/",
        views.teamlead_dashboard,
        name="teamlead_dashboard"
    ),

    path(
        "mytask/",
        views.mytask,
        name="mytask"
    ),

]
