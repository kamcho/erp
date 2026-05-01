from .models import School

def user_flags_processor(request):
    if request.user.is_authenticated:
        # Create a list of tuples for easy iteration in templates
        # (flag_name, label, current_status)
        flags_info = [
            ('is_headteacher', 'Headteacher', request.user.is_headteacher),
            ('is_exam_manager', 'Exam Manager', request.user.is_exam_manager),
            ('is_exam_officer', 'Exam Officer', request.user.is_exam_officer),
            ('is_staff', 'Staff Member', request.user.is_staff),
        ]
        context = {'flags_info': flags_info}
        if request.user.is_superuser:
            context['all_schools_dropdown'] = School.objects.all().order_by('name')
        return context
    return {}
