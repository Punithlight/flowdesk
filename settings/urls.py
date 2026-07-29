from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.settings_page,
        name="settings",
    ),

    path(
        "save/",
        views.settings_save,
        name="settings_save",
    ),

    path(
        "change-password/",
        views.settings_change_password,
        name="settings_change_password",
    ),

    path(
        "logout-all/",
        views.logout_all_devices,
        name="logout_all_devices",
    ),
]