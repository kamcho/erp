from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import Grade, School
from .models import SchoolCharge


def _can_manage_school_charges(user):
    return user.is_superuser or user.role in ["Admin", "Accountant", "Receptionist"]


def _can_edit_school_charges(user):
    return user.is_superuser


def _find_grade_conflict(school, name, grade_ids, exclude_pk=None):
    if not grade_ids:
        return None

    qs = SchoolCharge.objects.filter(
        school=school,
        name=name,
        grades__id__in=grade_ids,
    ).prefetch_related("grades").distinct()

    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    conflict = qs.first()
    if not conflict:
        return None

    existing_grade_ids = set(conflict.grades.values_list("id", flat=True))
    overlap_ids = [gid for gid in grade_ids if gid.isdigit() and int(gid) in existing_grade_ids]
    overlap_grades = Grade.objects.filter(id__in=overlap_ids).values_list("name", flat=True)
    overlap_label = ", ".join(overlap_grades) if overlap_ids else "selected grade(s)"
    return overlap_label


def _build_metadata_from_inputs(post_data, amount):
    """
    Build metadata from non-technical key/value inputs.
    Allowed keys: between, weekly, monthly, termly
    """
    key_map = {
        "between": "meta_between",
        "weekly": "meta_weekly",
        "monthly": "meta_monthly",
        "termly": "meta_termly",
    }
    day_counts = {
        "weekly": Decimal("5"),
        "monthly": Decimal("30"),
        "termly": Decimal("90"),
    }

    normalized_amounts = {}
    for key, field_name in key_map.items():
        raw_value = (post_data.get(field_name) or "").strip()
        if not raw_value:
            continue
        try:
            value = Decimal(raw_value)
        except (InvalidOperation, TypeError, ValueError):
            return None, f"Value for '{key}' must be a valid number."

        if value <= 0:
            return None, f"Value for '{key}' must be greater than zero."

        if key in day_counts:
            normal_total = amount * day_counts[key]
            if value > normal_total:
                return None, f"Value for '{key}' cannot exceed normal total ({normal_total})."

        normalized_amounts[key] = float(value)

    return {"full_amounts": normalized_amounts}, None


@login_required
def school_charges_list(request):
    if not _can_manage_school_charges(request.user):
        messages.error(request, "Permission denied.")
        return redirect("core:dashboard")

    charges = SchoolCharge.objects.select_related("school").prefetch_related("grades").order_by("-created_at")
    schools_qs = School.objects.all().order_by("name")

    if request.user.school_id:
        charges = charges.filter(school_id=request.user.school_id)
        schools_qs = schools_qs.filter(id=request.user.school_id)

    q = request.GET.get("q", "").strip()
    selected_school = request.GET.get("school", "").strip()
    if q:
        charges = charges.filter(Q(name__icontains=q) | Q(school__name__icontains=q))
    if selected_school:
        charges = charges.filter(school_id=selected_school)

    if request.method == "POST":
        if not _can_edit_school_charges(request.user):
            messages.error(request, "Only superusers can create school charges.")
            return redirect("cafe:schoolcharge-list")

        school_id = request.POST.get("school")
        name = request.POST.get("name", "").strip()
        amount_raw = request.POST.get("amount", "").strip()
        grade_ids = request.POST.getlist("grades")

        if not school_id or not name or not amount_raw:
            messages.error(request, "School, name and amount are required.")
            return redirect("cafe:schoolcharge-list")

        try:
            amount = Decimal(amount_raw)
        except InvalidOperation:
            messages.error(request, "Amount must be a valid number.")
            return redirect("cafe:schoolcharge-list")

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")
            return redirect("cafe:schoolcharge-list")

        school = get_object_or_404(schools_qs, id=school_id)
        overlap_label = _find_grade_conflict(school, name, grade_ids)
        if overlap_label:
            messages.error(
                request,
                f"Duplicate grade assignment for '{name}' in {school.name}. Already assigned grade(s): {overlap_label}.",
            )
            return redirect("cafe:schoolcharge-list")

        meta_data, meta_error = _build_metadata_from_inputs(request.POST, amount)
        if meta_error:
            messages.error(request, meta_error)
            return redirect("cafe:schoolcharge-list")

        charge = SchoolCharge.objects.create(
            school=school,
            name=name,
            amount=amount,
            meta_data=meta_data,
        )

        if grade_ids:
            grades = Grade.objects.filter(id__in=grade_ids)
            charge.grades.set(grades)

        messages.success(request, f"School charge '{name}' created successfully.")
        return redirect("cafe:schoolcharge-list")

    context = {
        "charges": charges,
        "schools": schools_qs,
        "grades": Grade.objects.all().order_by("name"),
        "q": q,
        "selected_school": selected_school,
        "can_edit": _can_edit_school_charges(request.user),
    }
    return render(request, "cafe/schoolcharge_list.html", context)


@login_required
@require_POST
def school_charge_update(request, pk):
    if not _can_edit_school_charges(request.user):
        messages.error(request, "Only superusers can edit school charges.")
        return redirect("core:dashboard")

    charge = get_object_or_404(SchoolCharge, pk=pk)
    if request.user.school_id and charge.school_id != request.user.school_id:
        messages.error(request, "Permission denied for this school.")
        return redirect("cafe:schoolcharge-list")

    school_qs = School.objects.filter(id=request.user.school_id) if request.user.school_id else School.objects.all()

    school_id = request.POST.get("school")
    name = request.POST.get("name", "").strip()
    amount_raw = request.POST.get("amount", "").strip()
    grade_ids = request.POST.getlist("grades")

    if not school_id or not name or not amount_raw:
        messages.error(request, "School, name and amount are required.")
        return redirect("cafe:schoolcharge-list")

    try:
        amount = Decimal(amount_raw)
    except InvalidOperation:
        messages.error(request, "Amount must be a valid number.")
        return redirect("cafe:schoolcharge-list")

    if amount <= 0:
        messages.error(request, "Amount must be greater than zero.")
        return redirect("cafe:schoolcharge-list")

    school = get_object_or_404(school_qs, id=school_id)
    overlap_label = _find_grade_conflict(school, name, grade_ids, exclude_pk=charge.pk)
    if overlap_label:
        messages.error(
            request,
            f"Duplicate grade assignment for '{name}' in {school.name}. Already assigned grade(s): {overlap_label}.",
        )
        return redirect("cafe:schoolcharge-list")
    meta_data, meta_error = _build_metadata_from_inputs(request.POST, amount)
    if meta_error:
        messages.error(request, meta_error)
        return redirect("cafe:schoolcharge-list")

    charge.school = school
    charge.name = name
    charge.amount = amount
    charge.meta_data = meta_data
    charge.save()
    charge.grades.set(Grade.objects.filter(id__in=grade_ids))

    messages.success(request, f"School charge '{charge.name}' updated successfully.")
    return redirect("cafe:schoolcharge-list")


@login_required
@require_POST
def school_charge_delete(request, pk):
    if not _can_edit_school_charges(request.user):
        messages.error(request, "Only superusers can delete school charges.")
        return redirect("core:dashboard")

    charge = get_object_or_404(SchoolCharge, pk=pk)
    if request.user.school_id and charge.school_id != request.user.school_id:
        messages.error(request, "Permission denied for this school.")
        return redirect("cafe:schoolcharge-list")

    charge_name = charge.name
    charge.delete()
    messages.success(request, f"School charge '{charge_name}' deleted successfully.")
    return redirect("cafe:schoolcharge-list")
