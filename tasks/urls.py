from django.urls import path
from . import views

urlpatterns = [

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
     path("export/", views.export, name="export"),

]