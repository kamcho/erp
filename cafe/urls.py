from django.urls import path

from . import views

app_name = "cafe"

urlpatterns = [
    path("school-charges/", views.school_charges_list, name="schoolcharge-list"),
    path("school-charges/<int:pk>/update/", views.school_charge_update, name="schoolcharge-update"),
    path("school-charges/<int:pk>/delete/", views.school_charge_delete, name="schoolcharge-delete"),
]
