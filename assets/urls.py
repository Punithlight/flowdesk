from django.urls import path
from . import views

urlpatterns = [

    path(
        "my-assets/",
        views.my_assets,
        name="my_assets",
    ),

]