from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import EmployeeAsset
from employees.models import Employee

@login_required
def my_assets(request):

    print("Logged User:", request.user)
    print("User ID:", request.user.id)

    employee = Employee.objects.get(user=request.user)

    assets = EmployeeAsset.objects.filter(employee=employee)

    print("Assets:", list(assets.values()))   # Debug line

    return render(
        request,
        "assets/myassets.html",
        {
            "assets": assets,
            "employee": employee,
        },
    )


@login_required
def manager_assets(request):
    employee = Employee.objects.get(user=request.user)
    assets = EmployeeAsset.objects.filter(employee=employee)
    return render(
        request,
        "assets/managerassets.html",
        {
            "assets": assets,
            "employee": employee,
        },
    )

# @login_required
# def teamlead_assets(request):
#     employee = Employee.objects.get(user=request.user)
#     assets = EmployeeAsset.objects.filter(employee=employee)
#     return render(
#         request,
#         "assets/teamleadassets.html",
#         {
#             "assets": assets,
#             "employee": employee,
#         },
#     )