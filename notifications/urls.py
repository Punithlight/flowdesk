from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.notification_list,
        name="notifications"
    ),
     path(
        "manager/",
        views.manager_notifications,
        name="manager_notifications"
    ),

]