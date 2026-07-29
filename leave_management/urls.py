from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.leave_dashboard,
        name="leave_dashboard"
    ),

]