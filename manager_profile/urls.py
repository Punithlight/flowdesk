from django.urls import path
from . import views

urlpatterns = [
    path("profile/",        views.manager_profile,    name="manager_profile"),
    path("edit/",           views.edit_profile,       name="manager_edit_profile"),
    path("personal-info/",  views.personal_info,      name="manager_personal_info"),
    path("update-details/", views.update_details,     name="manager_update_details"),
    path("change-password/",views.change_password,    name="manager_change_password"),
]
