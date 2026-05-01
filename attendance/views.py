from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from core.models import School, Student, AttendanceSession, StudentAttendance, StudentProfile
from .models import Device, LateTimeRule
from .serializers import AttendanceLogPayloadSerializer

class AttendanceLogUploadView(APIView):
    """
    API endpoint for receiving and processing attendance logs from biometric devices.
    Includes automated lateness detection based on school-defined rules.
    """
    def post(self, request, *args, **kwargs):
        serializer = AttendanceLogPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        school_id = data['school_id']
        device_id = data['device_id']
        logs = data['logs']

        if not logs:
            return Response({"error": "Logs array is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate School and Device
        try:
            school = School.objects.get(id=school_id)
        except (School.DoesNotExist, ValueError):
            return Response({"error": f"School with ID {school_id} not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id, school=school)
            device.save() # Update last_sync
        except (Device.DoesNotExist, ValueError):
            return Response({"error": f"Device {device_id} not found for school {school.name}"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Get Late Time Rules for this school
        # Map grade_id -> late_time (Time object)
        late_rules = {}
        rules = LateTimeRule.objects.filter(school=school).prefetch_related('grades')
        for rule in rules:
            for grade in rule.grades.all():
                late_rules[grade.id] = rule.late_time

        results = {
            "status": "success",
            "processed": 0,
            "skipped": 0,
            "errors": []
        }

        # 3. Extract all student IDs to minimize queries
        student_ids = [log['user_id'] for log in logs]
        # Map student IDs to Student objects along with their profile/grade/class
        students_map = {
            str(s.id): s for s in Student.objects.filter(id__in=student_ids).select_related('studentprofile__class_id__grade')
        }

        # 4. Process logs
        for log in logs:
            user_id = log['user_id']
            timestamp = log['timestamp']
            date = timestamp.date()
            time = timestamp.time()

            # Validate Student
            student = students_map.get(str(user_id))
            if not student:
                results["errors"].append({
                    "log": log,
                    "error": "Student not found"
                })
                continue

            # Check if student has a profile and class
            try:
                profile = student.studentprofile
                student_class = profile.class_id
                if not student_class:
                    results["errors"].append({
                        "log": log,
                        "error": "Student has no class assigned"
                    })
                    continue
            except StudentProfile.DoesNotExist:
                results["errors"].append({
                    "log": log,
                    "error": "Student has no profile"
                })
                continue

            # Determine Status (Present vs Late)
            # Find rule for this student's grade
            late_status = 'Present'
            grade_id = student_class.grade_id
            if grade_id in late_rules:
                if time > late_rules[grade_id]:
                    late_status = 'Late'

            try:
                with transaction.atomic():
                    # 5. Find or Create Attendance Session for the specific class and date
                    session, created = AttendanceSession.objects.get_or_create(
                        class_id=student_class,
                        date=date,
                        defaults={'taken_by': None}
                    )

                    # 6. Idempotency Check
                    if StudentAttendance.objects.filter(session=session, student=student).exists():
                        results["skipped"] += 1
                        continue

                    # 7. Create Attendance Record
                    StudentAttendance.objects.create(
                        session=session,
                        student=student,
                        status=late_status,
                        arrival_time=timestamp,
                        remarks=f'Logged via biometric device (Time: {time.strftime("%H:%M")})'
                    )

                    results["processed"] += 1

            except Exception as e:
                results["errors"].append({
                    "log": log,
                    "error": str(e)
                })

        return Response(results, status=status.HTTP_200_OK if results["processed"] > 0 or results["skipped"] > 0 else status.HTTP_207_MULTI_STATUS)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models import Grade, School

def _can_manage_late_rules(user):
    return user.is_superuser or user.role in ["Admin"]

def _find_late_rule_conflict(school, grade_ids, exclude_pk=None):
    if not grade_ids:
        return None
    
    qs = LateTimeRule.objects.filter(
        school=school,
        grades__id__in=grade_ids
    ).prefetch_related("grades").distinct()

    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    conflict = qs.first()
    if not conflict:
        return None
    
    # Find which specific grade is conflicting
    existing_grade_ids = set(conflict.grades.values_list("id", flat=True))
    overlap_ids = [gid for gid in grade_ids if int(gid) in existing_grade_ids]
    overlap_grades = Grade.objects.filter(id__in=overlap_ids).values_list("name", flat=True)
    overlap_label = ", ".join(overlap_grades)
    return f"Grade(s) {overlap_label} already assigned to rule '{conflict.name}'"

@login_required

def school_late_time_rules(request):
    if not _can_manage_late_rules(request.user):
        messages.error(request, "Permission denied.")
        return redirect("core:dashboard")

    rules = LateTimeRule.objects.select_related("school").prefetch_related("grades").order_by("name")
    schools_qs = School.objects.all().order_by("name")
    grades_qs = Grade.objects.all().order_by("name")

    if request.user.school_id:
        rules = rules.filter(school_id=request.user.school_id)
        schools_qs = schools_qs.filter(id=request.user.school_id)

    if request.method == "POST":
        school_id = request.POST.get("school")
        name = request.POST.get("name", "").strip()
        late_time = request.POST.get("late_time")
        grade_ids = request.POST.getlist("grades")

        if not school_id or not name or not late_time:
            messages.error(request, "School, Name and Late Time are required.")
            return redirect("attendance:late-rules-list")

        school = get_object_or_404(schools_qs, id=school_id)
        
        # Conflict Check
        conflict_msg = _find_late_rule_conflict(school, grade_ids)
        if conflict_msg:
            messages.error(request, conflict_msg)
            return redirect("attendance:late-rules-list")

        rule = LateTimeRule.objects.create(
            school=school,
            name=name,
            late_time=late_time
        )
        if grade_ids:
            rule.grades.set(Grade.objects.filter(id__in=grade_ids))

        messages.success(request, f"Late time rule '{name}' created successfully.")
        return redirect("attendance:late-rules-list")

    context = {
        "rules": rules,
        "schools": schools_qs,
        "grades": grades_qs,
        "can_edit": _can_manage_late_rules(request.user),
    }
    return render(request, "attendance/late_time_rules.html", context)

@login_required
@require_POST
def late_time_rule_update(request, pk):
    if not _can_manage_late_rules(request.user):
        messages.error(request, "Permission denied.")
        return redirect("core:dashboard")

    rule = get_object_or_404(LateTimeRule, pk=pk)
    if request.user.school_id and rule.school_id != request.user.school_id:
        messages.error(request, "Permission denied for this school.")
        return redirect("attendance:late-rules-list")

    name = request.POST.get("name", "").strip()
    late_time = request.POST.get("late_time")
    grade_ids = request.POST.getlist("grades")

    if not name or not late_time:
        messages.error(request, "Name and Late Time are required.")
        return redirect("attendance:late-rules-list")

    # Conflict Check
    conflict_msg = _find_late_rule_conflict(rule.school, grade_ids, exclude_pk=rule.pk)
    if conflict_msg:
        messages.error(request, conflict_msg)
        return redirect("attendance:late-rules-list")

    rule.name = name
    rule.late_time = late_time
    rule.save()

    rule.grades.set(Grade.objects.filter(id__in=grade_ids))

    messages.success(request, f"Late time rule '{name}' updated successfully.")
    return redirect("attendance:late-rules-list")

@login_required
@require_POST
def late_time_rule_delete(request, pk):
    if not _can_manage_late_rules(request.user):
        messages.error(request, "Permission denied.")
        return redirect("core:dashboard")

    rule = get_object_or_404(LateTimeRule, pk=pk)
    if request.user.school_id and rule.school_id != request.user.school_id:
        messages.error(request, "Permission denied for this school.")
        return redirect("attendance:late-rules-list")

    rule_name = rule.name
    rule.delete()
    messages.success(request, f"Late time rule '{rule_name}' deleted successfully.")
    return redirect("attendance:late-rules-list")

