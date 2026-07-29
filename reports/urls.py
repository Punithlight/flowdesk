from django.urls import path
from . import views


urlpatterns = [

    path(
        "task_report/",
        views.task_report,
        name="task_report"
    ),

]