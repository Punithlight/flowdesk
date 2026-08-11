
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.teamlead_profile,
        name="teamlead_profile"
    ),

   
]