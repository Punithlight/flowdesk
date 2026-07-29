from django.urls import path
from . import views


urlpatterns = [

    path(
        "Myprojects/",
        views.Myprojects,
        name="Myprojects"
    ),
    path(
        'create/',
        views.create_project,
        name='create_project'
    ),


]