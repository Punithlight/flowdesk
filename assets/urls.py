from django.urls import path
from . import views

urlpatterns = [

    path(
        "my-assets/",
        views.my_assets,
        name="my_assets",
    ),

    path(
        "manager-assets/",
        views.manager_assets,
        name="manager_assets",
    ),

]