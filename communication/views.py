from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, PaymentNotification, SMSLog
from core.models import School, Grade, Student
from django.db.models import Q

from .sms_utils import TextSMSAPI
from users.models import MyUser

from django.db.models import Count, Case, When, Value, IntegerField

@login_required
def notification_dashboard(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    notifications = Notification.objects.select_related('school', 'grade', 'created_by').annotate(
        success_count=Count(
            Case(When(sms_logs__status='Success', then=Value(1)), output_field=IntegerField())
        ),
        failed_count=Count(
            Case(When(sms_logs__status='Failed', then=Value(1)), output_field=IntegerField())
        )
    ).order_by('-created_at')
    
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) | 
            Q(message__icontains=search_query)
        )
    
    # SMS Logs with filtering
    sms_logs = SMSLog.objects.select_related('notification').order_by('-timestamp')
    
    if search_query:
        sms_logs = sms_logs.filter(
            Q(recipient__icontains=search_query) | 
            Q(message__icontains=search_query) |
            Q(message_id__icontains=search_query)
        )
    
    if status_filter:
        sms_logs = sms_logs.filter(status=status_filter)
        
    if date_from:
        sms_logs = sms_logs.filter(timestamp__date__gte=date_from)
    if date_to:
        sms_logs = sms_logs.filter(timestamp__date__lte=date_to)
        
    # Get recent SMS logs to show failure/success (limit after filtering)
    sms_logs_display = sms_logs[:100]
    
    schools = School.objects.all()
    grades = Grade.objects.all()
    
    from django.core.cache import cache
    
    # Cache SMS balance to prevent slow external API calls on every page load
    sms_balance = cache.get('sms_balance')
    if sms_balance is None:
        try:
            sms_api = TextSMSAPI()
            sms_balance = sms_api.get_balance()
            cache.set('sms_balance', sms_balance, 300) # Cache for 5 minutes
        except Exception:
            sms_balance = "N/A"
    
    # Cache heavy database counts
    students_count = cache.get('active_students_count')
    if students_count is None:
        students_count = Student.objects.filter(studentprofile__status='Active').count()
        cache.set('active_students_count', students_count, 900) # Cache for 15 minutes
        
    guardians_count = cache.get('unique_guardians_count')
    if guardians_count is None:
        guardians_count = MyUser.objects.filter(students__isnull=False).distinct().count()
        cache.set('unique_guardians_count', guardians_count, 900) # Cache for 15 minutes

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_notification':
            title = request.POST.get('title')
            message = request.POST.get('message')
            target_type = request.POST.get('target_type')
            school_id = request.POST.get('school_id')
            grade_id = request.POST.get('grade_id')
            
            school = School.objects.get(id=school_id) if school_id else None
            grade = Grade.objects.get(id=grade_id) if grade_id else None
            
            notification = Notification.objects.create(
                title=title,
                message=message,
                target_type=target_type,
                school=school,
                grade=grade,
                created_by=request.user
            )
            
            # Identify recipients
            students = Student.objects.filter(studentprofile__status='Active')
            
            if target_type == 'certain_school' and school:
                students = students.filter(studentprofile__school=school)
            elif target_type == 'grade_all_schools' and grade:
                students = students.filter(studentprofile__class_id__grade=grade)
            elif target_type == 'grade_certain_school' and school and grade:
                students = students.filter(studentprofile__school=school, studentprofile__class_id__grade=grade)
            
            # Fetch guardians (any linked user) for these students
            guardians = MyUser.objects.filter(students__in=students).distinct()
            
            sms_api = TextSMSAPI()
            sent_count = 0
            fail_count = 0
            
            for guardian in guardians:
                if guardian.phone_number:
                    success, info = sms_api.send_sms(guardian.phone_number, message, notification=notification)
                    if success:
                        sent_count += 1
                    else:
                        fail_count += 1
            
            msg = f"Notification created. Sent {sent_count} SMS messages."
            if fail_count > 0:
                msg += f" Failed to send {fail_count} messages."
                messages.warning(request, msg)
            else:
                messages.success(request, msg)
                from core.activity_log import log_activity
                log_activity(request.user, 'Broadcast', 'Communication', f'Sent broadcast "{title}" to {sent_count} recipients.', 'Notification', notification.pk)
                
            return redirect('communication:dashboard')

    return render(request, 'communication/dashboard.html', {
        'notifications': notifications,
        'sms_logs': sms_logs_display,
        'sms_balance': sms_balance,
        'students_count': students_count,
        'guardians_count': guardians_count,
        'schools': schools,
        'grades': grades,
        'target_choices': Notification.TARGET_CHOICES,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_logs_count': sms_logs.count()
    })

@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.delete()
    messages.success(request, "Notification deleted.")
    return redirect('communication:dashboard')

@login_required
def resend_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    
    if request.method == 'POST':
        failed_logs = notification.sms_logs.filter(status='Failed')
        success_recipients = notification.sms_logs.filter(status='Success').values_list('recipient', flat=True)
        
        failed_recipients_logs = failed_logs.exclude(recipient__in=success_recipients)
        
        unique_failed = {}
        for log in failed_recipients_logs:
            unique_failed[log.recipient] = log.message
            
        if not unique_failed:
            messages.info(request, "No failed messages to resend.")
            return redirect('communication:dashboard')

        sms_api = TextSMSAPI()
        sent_count = 0
        fail_count = 0
        
        for recipient, message in unique_failed.items():
            success, info = sms_api.send_sms(recipient, message, notification=notification)
            if success:
                sent_count += 1
            else:
                fail_count += 1
                
        msg = f"Resend complete. Sent {sent_count} successful messages."
        if fail_count > 0:
            msg += f" {fail_count} failed to send."
            messages.warning(request, msg)
        else:
            messages.success(request, msg)
            
    return redirect('communication:dashboard')

@login_required
def payment_notifications_list(request):
    p_notifications = PaymentNotification.objects.select_related('student', 'payment').order_by('-sent_at')
    return render(request, 'communication/payment_notifications.html', {
        'payment_notifications': p_notifications
    })

from django.http import JsonResponse

@login_required
@login_required
def guardian_notification_list(request):
    """View for parents to see notifications relevant to their students."""
    from users.models import MyUser
    
    # Get all students linked to this guardian
    students = request.user.students.all().select_related('studentprofile__school', 'studentprofile__class_id__grade')
    
    if not students:
        return render(request, 'communication/guardian_notifications.html', {
            'notifications': [],
            'students': []
        })

    # Collect all relevant school IDs and grade IDs for these students
    school_ids = set()
    grade_ids = set()
    student_grade_school_pairs = set()

    for student in students:
        profile = getattr(student, 'studentprofile', None)
        if profile:
            if profile.school:
                school_ids.add(profile.school.id)
            if profile.class_id and profile.class_id.grade:
                grade_ids.add(profile.class_id.grade.id)
                if profile.school:
                    student_grade_school_pairs.add((profile.school.id, profile.class_id.grade.id))

    # Base query for notifications
    # Filter based on target_type and corresponding IDs
    q_objects = Q(target_type='all_schools')
    
    if school_ids:
        q_objects |= Q(target_type='certain_school', school_id__in=school_ids)
    
    if grade_ids:
        q_objects |= Q(target_type='grade_all_schools', grade_id__in=grade_ids)
        
    # For grade_certain_school, we check if the combination exists
    if student_grade_school_pairs:
        for school_id, grade_id in student_grade_school_pairs:
            q_objects |= Q(target_type='grade_certain_school', school_id=school_id, grade_id=grade_id)

    notifications = Notification.objects.filter(q_objects).select_related('school', 'grade', 'created_by').order_by('-created_at')

    # Apply search filter
    search_query = request.GET.get('q', '')
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) | 
            Q(message__icontains=search_query)
        )

    return render(request, 'communication/guardian_notifications.html', {
        'notifications': notifications,
        'search_query': search_query,
        'students': students
    })

def get_recipients_count(request):
    target_type = request.GET.get('target_type')
    school_id = request.GET.get('school_id')
    grade_id = request.GET.get('grade_id')
    
    students = Student.objects.filter(studentprofile__status='Active')
    
    if target_type == 'certain_school' and school_id:
        students = students.filter(studentprofile__school_id=school_id)
    elif target_type == 'grade_all_schools' and grade_id:
        students = students.filter(studentprofile__class_id__grade_id=grade_id)
    elif target_type == 'grade_certain_school' and school_id and grade_id:
        students = students.filter(studentprofile__school_id=school_id, studentprofile__class_id__grade_id=grade_id)
        
    guardians_count = MyUser.objects.filter(students__in=students, phone_number__isnull=False).exclude(phone_number='').distinct().count()
    return JsonResponse({'guardians_count': guardians_count})


@login_required
def send_results_sms(request):
    """View for sending exam results to parents via SMS, filtered per grade."""
    from Exam.models import Exam, ExamSubjectConfiguration, ExamSUbjectScore
    from core.models import School, Grade
    from .models import ResultSMSDispatch

    schools = School.objects.all()
    grades = Grade.objects.all()
    exams = Exam.objects.select_related('year', 'term').order_by('-created_at')

    selected_exam_id = request.GET.get('exam_id') or request.POST.get('exam_id')
    selected_grade_id = request.GET.get('grade_id') or request.POST.get('grade_id')
    selected_school_id = request.GET.get('school_id') or request.POST.get('school_id')

    preview_students = []
    selected_exam = None
    selected_grade = None
    selected_school = None
    dispatch_summary = None

    if selected_exam_id and selected_grade_id:
        selected_exam = Exam.objects.filter(id=selected_exam_id).first()
        selected_grade = Grade.objects.filter(id=selected_grade_id).first()
        if selected_school_id:
            selected_school = School.objects.filter(id=selected_school_id).first()

        if selected_exam and selected_grade:
            students_qs = Student.objects.filter(
                studentprofile__status='Active',
                studentprofile__class_id__grade=selected_grade
            ).select_related('studentprofile', 'studentprofile__class_id', 'studentprofile__school')

            if selected_school:
                students_qs = students_qs.filter(studentprofile__school=selected_school)

            subject_configs = ExamSubjectConfiguration.objects.filter(
                exam=selected_exam,
                subject__grade=selected_grade.name
            ).select_related('subject')

            # Pre-fetch all existing dispatches for this exam to avoid N+1 queries
            existing_dispatches = ResultSMSDispatch.objects.filter(
                exam=selected_exam,
                student__in=students_qs
            ).select_related('guardian').values('student_id', 'guardian_id', 'status', 'recipient_phone', 'dispatched_at')

            # Map: student_id -> list of dispatch dicts
            dispatch_map = {}
            for d in existing_dispatches:
                dispatch_map.setdefault(d['student_id'], []).append(d)

            for student in students_qs:
                scores = ExamSUbjectScore.objects.filter(
                    student=student,
                    paper__exam_subject__exam=selected_exam,
                    paper__exam_subject__subject__grade=selected_grade.name
                ).select_related('paper__exam_subject__subject')

                if not scores.exists():
                    continue

                subject_results = []
                total_score = 0
                total_max = 0
                for config in subject_configs:
                    student_scores = scores.filter(paper__exam_subject=config)
                    if student_scores.exists():
                        combined_score = sum(s.score for s in student_scores)
                        grade_val = student_scores.first().grade
                        subject_results.append({
                            'name': config.subject.name,
                            'abbr': config.subject.name[:4].upper(),
                            'score': combined_score,
                            'max': config.max_score,
                            'grade': grade_val
                        })
                        total_score += combined_score
                        total_max += config.max_score

                guardians = MyUser.objects.filter(
                    students=student,
                    phone_number__isnull=False
                ).exclude(phone_number='').distinct()

                if not subject_results or not guardians.exists():
                    continue

                avg_pct = round((total_score / total_max) * 100) if total_max > 0 else 0
                results_lines = [f"{r['abbr']}:{r['score']}/{r['max']}({r['grade']})" for r in subject_results]
                sms_message = (
                    f"Dear Parent, {student.first_name} {student.last_name}'s "
                    f"{selected_exam.name} Results:\n"
                    f"{', '.join(results_lines)}\n"
                    f"Total: {total_score}/{total_max} ({avg_pct}%)\n"
                    f"Thank you."
                )

                # Determine send status per guardian
                student_dispatches = dispatch_map.get(student.id, [])
                guardian_status = {}
                for d in student_dispatches:
                    guardian_status[d['guardian_id']] = d

                # Overall status for the student
                sent_count_ok = sum(1 for d in student_dispatches if d['status'] == 'Success')
                sent_count_fail = sum(1 for d in student_dispatches if d['status'] == 'Failed')
                total_guardians = guardians.count()

                if not student_dispatches:
                    overall_status = 'not_sent'
                elif sent_count_ok == total_guardians:
                    overall_status = 'sent_ok'
                elif sent_count_fail == total_guardians:
                    overall_status = 'sent_failed'
                else:
                    overall_status = 'sent_partial'

                preview_students.append({
                    'student': student,
                    'guardians': guardians,
                    'subject_results': subject_results,
                    'total_score': total_score,
                    'total_max': total_max,
                    'avg_pct': avg_pct,
                    'sms_message': sms_message,
                    'char_count': len(sms_message),
                    'overall_status': overall_status,
                    'sent_count_ok': sent_count_ok,
                    'sent_count_fail': sent_count_fail,
                    'guardian_status': guardian_status,
                    'dispatches': student_dispatches,
                })

            # Compute summary counts
            if preview_students:
                dispatch_summary = {
                    'not_sent': sum(1 for p in preview_students if p['overall_status'] == 'not_sent'),
                    'sent_ok': sum(1 for p in preview_students if p['overall_status'] == 'sent_ok'),
                    'sent_failed': sum(1 for p in preview_students if p['overall_status'] == 'sent_failed'),
                    'sent_partial': sum(1 for p in preview_students if p['overall_status'] == 'sent_partial'),
                    'total': len(preview_students),
                }

    def _build_and_send(students_preview, selected_exam, selected_grade, selected_school, notification, action_type):
        """Helper: sends SMS and records ResultSMSDispatch. Returns (sent, failed)."""
        sms_api = TextSMSAPI()
        sent_count = 0
        fail_count = 0
        for preview in students_preview:
            for guardian in preview['guardians']:
                # For resend: skip already successful ones
                if action_type == 'resend_failed':
                    existing = ResultSMSDispatch.objects.filter(
                        student=preview['student'], exam=selected_exam, guardian=guardian
                    ).first()
                    if existing and existing.status == 'Success':
                        continue

                success, info = sms_api.send_sms(
                    guardian.phone_number,
                    preview['sms_message'],
                    notification=notification
                )
                status_val = 'Success' if success else 'Failed'
                if success:
                    sent_count += 1
                else:
                    fail_count += 1

                # Get the last SMSLog entry for this recipient
                last_log = SMSLog.objects.filter(recipient__icontains=guardian.phone_number).order_by('-timestamp').first()

                ResultSMSDispatch.objects.update_or_create(
                    student=preview['student'],
                    exam=selected_exam,
                    guardian=guardian,
                    defaults={
                        'recipient_phone': guardian.phone_number,
                        'message': preview['sms_message'],
                        'status': status_val,
                        'sms_log': last_log,
                        'dispatched_by': request.user,
                        'notification': notification,
                    }
                )
        return sent_count, fail_count

    # POST: Send all not-yet-sent results
    if request.method == 'POST' and request.POST.get('action') == 'send_results':
        to_send = [p for p in preview_students if p['overall_status'] == 'not_sent']
        if not to_send:
            messages.warning(request, "No new students to send — all results already dispatched. Use 'Resend Failed' to retry failures.")
            return redirect(f"{request.path}?exam_id={selected_exam_id}&grade_id={selected_grade_id}&school_id={selected_school_id or ''}")

        notification = Notification.objects.create(
            title=f"Results SMS: {selected_exam.name} — {selected_grade.name}",
            message=f"Exam results dispatched for {selected_exam.name} to {selected_grade.name}",
            target_type='grade_certain_school' if selected_school else 'grade_all_schools',
            school=selected_school,
            grade=selected_grade,
            created_by=request.user
        )
        sent, failed = _build_and_send(to_send, selected_exam, selected_grade, selected_school, notification, 'send')
        msg = f"Dispatched results to {sent} guardians."
        if failed:
            msg += f" {failed} failed — use 'Resend Failed' to retry."
            messages.warning(request, msg)
        else:
            messages.success(request, msg)
        
        from core.activity_log import log_activity
        log_activity(request.user, 'Results Sent', 'Communication', f'Sent exam results for {selected_exam.name} ({selected_grade.name}) to {sent} recipients.', 'Exam', selected_exam.id)
        return redirect(f"{request.path}?exam_id={selected_exam_id}&grade_id={selected_grade_id}&school_id={selected_school_id or ''}")

    # POST: Resend only failed dispatches
    if request.method == 'POST' and request.POST.get('action') == 'resend_failed':
        failed_students = [p for p in preview_students if p['overall_status'] in ('sent_failed', 'sent_partial')]
        if not failed_students:
            messages.info(request, "No failed dispatches found to resend.")
            return redirect(f"{request.path}?exam_id={selected_exam_id}&grade_id={selected_grade_id}&school_id={selected_school_id or ''}")

        notification = Notification.objects.create(
            title=f"Results Resend: {selected_exam.name} — {selected_grade.name}",
            message=f"Resent failed results for {selected_exam.name} to {selected_grade.name}",
            target_type='grade_certain_school' if selected_school else 'grade_all_schools',
            school=selected_school,
            grade=selected_grade,
            created_by=request.user
        )
        sent, failed = _build_and_send(failed_students, selected_exam, selected_grade, selected_school, notification, 'resend_failed')
        msg = f"Resend complete: {sent} succeeded."
        if failed:
            msg += f" {failed} still failing."
            messages.warning(request, msg)
        else:
            messages.success(request, msg)
        return redirect(f"{request.path}?exam_id={selected_exam_id}&grade_id={selected_grade_id}&school_id={selected_school_id or ''}")

    # SMS balance
    from django.core.cache import cache
    sms_balance = cache.get('sms_balance')
    if sms_balance is None:
        try:
            sms_api_inst = TextSMSAPI()
            sms_balance = sms_api_inst.get_balance()
            cache.set('sms_balance', sms_balance, 300)
        except Exception:
            sms_balance = "N/A"

    not_sent_count = sum(1 for p in preview_students if p['overall_status'] == 'not_sent')
    failed_count = sum(1 for p in preview_students if p['overall_status'] in ('sent_failed', 'sent_partial'))

    return render(request, 'communication/send_results_sms.html', {
        'schools': schools,
        'grades': grades,
        'exams': exams,
        'preview_students': preview_students,
        'selected_exam': selected_exam,
        'selected_grade': selected_grade,
        'selected_school': selected_school,
        'sms_balance': sms_balance,
        'total_sms_count': sum(len(list(p['guardians'])) for p in preview_students if p['overall_status'] == 'not_sent'),
        'dispatch_summary': dispatch_summary,
        'not_sent_count': not_sent_count,
        'failed_count': failed_count,
    })


@login_required
def attendance_sms_logs(request):
    """View to see attendance SMS dispatches and resend failed ones."""
    from .models import AttendanceSMSDispatch, SMSLog
    from .sms_utils import TextSMSAPI
    from django.utils import timezone
    from django.core.cache import cache
    
    today = timezone.now().date()
    logs = AttendanceSMSDispatch.objects.select_related(
        'student', 'guardian', 'attendance_record', 'attendance_record__session__class_id'
    ).order_by('-dispatched_at')
    
    # Handle Individual Resend
    resend_id = request.POST.get('resend_id')
    if request.method == 'POST' and resend_id:
        dispatch = get_object_or_404(AttendanceSMSDispatch, id=resend_id)
        
        # Enforce today only
        if dispatch.dispatched_at.date() != today:
            messages.error(request, "Restriction: You can only resend messages originally sent today.")
            return redirect('communication:attendance-sms-logs')

        sms_api = TextSMSAPI()
        status, response = sms_api.send_sms(dispatch.recipient_phone, dispatch.message)
        
        log = SMSLog.objects.create(
            recipient=dispatch.recipient_phone,
            message=dispatch.message,
            status='Success' if status else 'Failed',
            response_description=str(response)
        )
        
        dispatch.status = 'Success' if status else 'Failed'
        dispatch.sms_log = log
        dispatch.save()
        
        if status:
            messages.success(request, f"Successfully resent message to {dispatch.recipient_phone}")
        else:
            messages.error(request, f"Resend failed for {dispatch.recipient_phone}")
        return redirect('communication:attendance-sms-logs')

    # Handle Bulk Resend (Today's Failures Only)
    if request.method == 'POST' and request.POST.get('action') == 'resend_failed':
        failed_dispatches = AttendanceSMSDispatch.objects.filter(status='Failed', dispatched_at__date=today)
        if not failed_dispatches:
            messages.info(request, "No failed attendance notifications from today to resend.")
            return redirect('communication:attendance-sms-logs')
            
        sms_api = TextSMSAPI()
        success_count = 0
        fail_count = 0
        
        for dispatch in failed_dispatches:
            status, response = sms_api.send_sms(dispatch.recipient_phone, dispatch.message)
            
            log = SMSLog.objects.create(
                recipient=dispatch.recipient_phone,
                message=dispatch.message,
                status='Success' if status else 'Failed',
                response_description=str(response)
            )
            
            dispatch.status = 'Success' if status else 'Failed'
            dispatch.sms_log = log
            dispatch.save()
            
            if status:
                success_count += 1
            else:
                fail_count += 1
                
        messages.success(request, f"Resend complete: {success_count} succeeded, {fail_count} still failing.")
        return redirect('communication:attendance-sms-logs')

    # SMS Balance
    sms_balance = cache.get('sms_balance')
    if sms_balance is None:
        try:
            sms_api_inst = TextSMSAPI()
            sms_balance = sms_api_inst.get_balance()
            cache.set('sms_balance', sms_balance, 300)
        except Exception:
            sms_balance = "N/A"

    # Filtering
    search = request.GET.get('q')
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    
    # Default to today if no filters are applied
    if not any([search, status_filter, date_filter]):
        date_filter = today.isoformat()

    if search:
        logs = logs.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(recipient_phone__icontains=search) |
            Q(message__icontains=search)
        )
        
    if status_filter:
        logs = logs.filter(status=status_filter)

    if date_filter:
        logs = logs.filter(dispatched_at__date=date_filter)

    return render(request, 'communication/attendance_sms_logs.html', {
        'logs': logs[:200],
        'failed_count': logs.filter(status='Failed').count(),
        'search_query': search or '',
        'status_filter': status_filter or '',
        'date_filter': date_filter or '',
        'sms_balance': sms_balance,
        'today': today
    })
