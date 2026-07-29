from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.employees_profile, name="employees_profile"),

    path("edit-profile/", views.edit_profile, name="edit_profile"),

    path("personal-info/", views.personal_info, name="personal_info"),

    path("update-details/", views.update_details, name="update_details"),

    path("change-password/", views.change_password, name="change_password"),
]