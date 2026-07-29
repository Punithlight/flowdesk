from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Project
from .forms import ProjectForm



@login_required
def Myprojects(request):

    projects = Project.objects.filter(
        employee=request.user
    )

    return render(
        request,
        "projects/Myprojects.html",
        {
            "projects": projects
        }
    )



@login_required
def create_project(request):

    if request.method == "POST":

        form = ProjectForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("Myprojects")

    else:

        form = ProjectForm()


    return render(
        request,
        "projects/create_project.html",
        {
            "form": form
        }
    )