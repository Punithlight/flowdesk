from django.contrib import admin
from .models import EmployeeAsset


@admin.register(EmployeeAsset)
class EmployeeAssetAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "asset_name",
        "asset_id",
        "status",
        "assigned_date",
    )

    search_fields = (
        "employee__user__username",
        "asset_name",
        "asset_id",
    )

    list_filter = (
        "status",
        "asset_name",
    )