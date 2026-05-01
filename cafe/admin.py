from django.contrib import admin
from .models import LunchSubscription, SchoolCharge


@admin.register(SchoolCharge)
class SchoolChargeAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "amount", "created_at")
    list_filter = ("school", "grades")
    search_fields = ("name", "school__name")
    filter_horizontal = ("grades",)


@admin.register(LunchSubscription)
class LunchSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("student", "school_charge", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "start_date", "end_date", "school_charge__school")
    search_fields = (
        "student__first_name",
        "student__middle_name",
        "student__last_name",
        "student__adm_no",
        "school_charge__name",
    )
